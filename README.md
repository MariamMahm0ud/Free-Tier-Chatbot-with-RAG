# Free-Tier Website Chatbot with RAG

A fully self-hostable chatbot system that scrapes a target website, builds a searchable knowledge base using local embeddings, and answers user questions using a Retrieval-Augmented Generation (RAG) pipeline. The entire system operates on free-tier and open-source components.

---

## 🚀 Key Features

-   **🤖 End-to-End RAG Pipeline**: Complete workflow from website scraping to a fully interactive chat UI.
-   **Polite Web Scraper**: Respects `robots.txt`, applies rate limiting, and avoids duplicate content.
-   **🧠 Local & Open-Source AI**: Uses `sentence-transformers` for embeddings and integrates with local LLMs (Phi-2) for generative answers.
-   **💾 Persistent Vector Store**: Leverages **ChromaDB** for efficient similarity search.
-   **📦 Fully Dockerized**: The entire application is orchestrated with **Docker Compose** for a reproducible one-command setup.
-   **🖥️ Integrated Web UI**: A clean interface built with **Gradio**, served directly through **FastAPI** for maximum stability.
-   **📄 Source Citations**: Provides source URLs for transparency.

---

## ⚙️ Tech Stack

-   **Backend**: Python, FastAPI
-   **Frontend**: Gradio
-   **Vector Database**: ChromaDB
-   **Embeddings Model**: `sentence-transformers/all-MiniLM-L6-v2`
-   **Orchestration**: Docker, Docker Compose
-   **Optional LLM**: GPT4All compatible models

---

## 🏁 Getting Started

### Prerequisites

-   Python 3.10+
-   Docker and Docker Compose
-   Git

### Initial Setup (Common for all Docker methods)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/MariamMahm0ud/Free-Tier-Chatbot-with-RAG
    cd Free-Tier-Chatbot-with-RAG

    ```
    

2.  **Set up the environment file:**
    ```bash
    cp .env.example .env
    ```

3.  **Download a Local LLM (Recommended):**
    -   Download a **modern, compatible model** (`Phi-2-GGUF `) from the [GPT4All Website](https://gpt4all.io).
    -   or [# Free-Tier-Chatbot-with-RAG](https://huggingface.co/TheBloke/phi-2-GGUF/blob/main/phi-2.Q4_K_M.gguf)
    -   and save on main project folder
    -   Open your `.env` file and set the `GPT4ALL_MODEL` variable to the relative path of the model.
    -   For example: `GPT4ALL_MODEL=phi-3-mini-instruct.gguf`

---

### Docker Method 1: Using the Quick Start Scripts (Easiest)

This method automates the build and run process.

1.  **Run the script for your OS:**
    -   **On Windows:** `.\docker-start.bat`
    -   **On Linux/macOS:** `chmod +x docker-start.sh && ./docker-start.sh`

2.  **Follow the on-screen instructions** to run the data processing steps (crawl, chunk, index).

3.  **Access the Chatbot:**
    -   **Web UI**: **[http://localhost:7860](http://localhost:7860)**

---

### Docker Method 2: Manual Docker Compose Commands (For More Control)

This method gives you a step-by-step understanding of the process.

1.  **Build the Docker Images:**
    This command reads the `Dockerfile` in each service directory and builds the necessary images.
    ```bash
    docker-compose build
    ```

2.  **Run the Data Pipeline (Step-by-Step):**
    These commands run one-off tasks in temporary containers to process your data.

    ```bash
    # Step 2a: Crawl the website
    docker-compose run --rm scraper python scraper/crawl.py

    # Step 2b: Clean and chunk the scraped content
    docker-compose run --rm scraper python scraper/clean_chunk.py

    # Step 2c: Generate embeddings and index the data
    # This runs the indexer in a temporary 'rag_service' container
    docker-compose run --rm rag_service python rag_service/indexer.py
    ```

3.  **Start the Application Services:**
    Once the data is indexed, start the main API and web services in the background.
    ```bash
    docker-compose up -d
    ```

4.  **Access the Chatbot:**
    -   **Web UI**: **[http://localhost:7860](http://localhost:7777)**
    -   **API Docs**: **[http://localhost:8000/docs](http://localhost:8000/docs)**

5.  **To Stop the Application:**
    ```bash
    docker-compose down
    ```

---

### Manual Installation (Without Docker)

This method is for local development and debugging.

1.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # On Windows
    # source venv/bin/activate  # On Linux/macOS
    ```

2.  **Install dependencies:**
    ```bash
    # IMPORTANT: Install the stable version of gpt4all first
    pip install gpt4all==2.8.1
    # Then install the rest
    pip install -r rag_service/requirements.txt
    ```

3.  **Run the Data Pipeline:**
    ```bash
    python scraper/crawl.py
    python scraper/clean_chunk.py
    python rag_service/indexer.py
    ```

4.  **Start the Integrated Server:**
    Run this single command to start FastAPI and Gradio together.
    ```bash
    uvicorn rag_service.api:app --host 0.0.0.0 --port 8000
    ```

5.  **Access the Chatbot:**
    -   Open your browser to **[http://localhost:7777](http://localhost:7777)**

---

## 🎥 Demo Video
Click the link below to download and watch the demo:

👉 [Download / Watch Demo](https://github.com/MariamMahm0ud/Free-Tier-Chatbot-with-RAG/raw/main/2025-11-16-05-40-25_ncKnjIwb.mkv)


## 💡 Troubleshooting

-   **`OSError: Cannot find empty port`**: The port is already in use. Choose a different port in your `uvicorn` command (e.g., `--port 8889`).
-   **`ModuleNotFoundError`**: Make sure you have activated your virtual environment (`venv`) first.
-   **LLM Not Working**:
    1.  Check the `gpt4all` version: Ensure you have the stable version (`2.8.1`).
    2.  Check the `.env` path to your model.
    3.  Ensure your machine has enough free **RAM**.
