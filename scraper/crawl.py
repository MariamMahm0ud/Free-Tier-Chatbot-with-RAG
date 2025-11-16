"""
BFS Web Crawler with robots.txt respect and rate limiting.
Scrapes a website, extracts main content using readability, and saves as JSON.
"""

import os
import json
import time
import hashlib
import urllib.robotparser
import urllib.parse
from collections import deque
from typing import Set, Dict, Optional
import requests
from readability import Document
from bs4 import BeautifulSoup

# Configuration
ROOT_URL = os.getenv("ROOT_URL", "https://quotes.toscrape.com/")
MAX_PAGES = int(os.getenv("MAX_PAGES", "200"))
RATE_LIMIT = float(os.getenv("RATE", "1.0"))  # seconds between requests
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
USER_AGENT = "RAG-Crawler/1.0"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_robots_parser(url: str) -> Optional[urllib.robotparser.RobotFileParser]:
    """Parse robots.txt for the given URL."""
    parsed = urllib.parse.urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp
    except Exception as e:
        print(f"Warning: Could not fetch robots.txt from {robots_url}: {e}")
        return None


def get_canonical_url(url: str) -> str:
    """Normalize URL to canonical form (remove fragments, normalize path)."""
    parsed = urllib.parse.urlparse(url)
    # Remove fragment, normalize path
    normalized = urllib.parse.urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path.rstrip('/') or '/',
        parsed.params,
        parsed.query,
        ''  # no fragment
    ))
    return normalized


def calculate_checksum(text: str) -> str:
    """Calculate MD5 checksum of text for deduplication."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def extract_content(url: str, html: str) -> Dict:
    """Extract main content from HTML using readability."""
    try:
        doc = Document(html)
        title = doc.title()
        content = doc.summary()
        
        # Clean HTML tags from content
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        
        return {
            "url": url,
            "title": title or "Untitled",
            "text": text,
            "status_code": 200
        }
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return {
            "url": url,
            "title": "Error",
            "text": "",
            "status_code": 200
        }


def crawl_website(root_url: str, max_pages: int, rate_limit: float) -> int:
    """
    BFS crawl starting from root_url.
    Returns number of pages saved.
    """
    visited: Set[str] = set()
    checksums: Set[str] = set()
    queue = deque([root_url])
    saved_count = 0
    
    # Get robots parser
    robots_parser = get_robots_parser(root_url)
    
    print(f"Starting crawl from {root_url}")
    print(f"Max pages: {max_pages}, Rate limit: {rate_limit}s")
    
    while queue and saved_count < max_pages:
        current_url = queue.popleft()
        canonical = get_canonical_url(current_url)
        
        if canonical in visited:
            continue
        
        # Check robots.txt
        if robots_parser and not robots_parser.can_fetch(USER_AGENT, canonical):
            print(f"Skipping {canonical} (disallowed by robots.txt)")
            visited.add(canonical)
            continue
        
        visited.add(canonical)
        
        # Rate limiting
        time.sleep(rate_limit)
        
        try:
            response = requests.get(
                canonical,
                headers={"User-Agent": USER_AGENT},
                timeout=10,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Extract content
            page_data = extract_content(canonical, response.text)
            checksum = calculate_checksum(page_data["text"])
            
            # Deduplicate by checksum
            if checksum in checksums:
                print(f"Skipping duplicate content: {canonical}")
                continue
            
            checksums.add(checksum)
            page_data["checksum"] = checksum
            
            # Save to JSON file
            filename = f"{saved_count:05d}_{checksum[:8]}.json"
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(page_data, f, ensure_ascii=False, indent=2)
            
            saved_count += 1
            print(f"[{saved_count}/{max_pages}] Saved: {canonical}")
            
            # Extract links for BFS (only if we haven't reached max)
            if saved_count < max_pages:
                try:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        absolute_url = urllib.parse.urljoin(canonical, href)
                        parsed = urllib.parse.urlparse(absolute_url)
                        
                        # Only follow same-domain links
                        root_parsed = urllib.parse.urlparse(root_url)
                        if parsed.netloc == root_parsed.netloc:
                            abs_canonical = get_canonical_url(absolute_url)
                            if abs_canonical not in visited:
                                queue.append(abs_canonical)
                except Exception as e:
                    print(f"Warning: Error extracting links from {canonical}: {e}")
        
        except requests.RequestException as e:
            print(f"Error fetching {canonical}: {e}")
            continue
        except Exception as e:
            print(f"Unexpected error processing {canonical}: {e}")
            continue
    
    print(f"\nCrawl completed. Saved {saved_count} pages to {OUTPUT_DIR}")
    return saved_count


if __name__ == "__main__":
    saved = crawl_website(ROOT_URL, MAX_PAGES, RATE_LIMIT)
    print(f"Total pages saved: {saved}")

