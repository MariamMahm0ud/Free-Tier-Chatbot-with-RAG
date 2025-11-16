


import json
import requests
import gradio as gr

API_URL = "http://127.0.0.1:8000"


def query_chatbot_streaming(query: str, use_streaming: bool, use_llm: bool):
    """
    Streaming query: yields answer and sources live for Gradio.
    Always uses the single available LLM model.
    """

    # =========================
    # STREAMING ENABLED
    # =========================
    if use_streaming:
        try:
            response = requests.post(
                f"{API_URL}/chat/stream",
                json={"query": query, "top_k": 5, "use_llm": use_llm},
                stream=True,
                timeout=200
            )
            response.raise_for_status()

            answer = ""
            sources_text = ""
            sources = []
              
            #seen_tokens = set()  # reset token cache for every streaming request
            globals()["last_fragment"] = ""  

            for line in response.iter_lines():
                if not line:
                    continue
                line_str = line.decode("utf-8")
                if not line_str.startswith("data: "):
                    continue
                try:
                    data = json.loads(line_str[6:])
                except json.JSONDecodeError:
                    continue


                if data.get("type") == "token":
                    token = data["content"]
                    answer += token  

                    fragment_buffer = answer[-200:]

                    last_safe_end = max(fragment_buffer.rfind(p) for p in [".", "!", "?", '"'])

                    if last_safe_end != -1:
                        current_fragment = fragment_buffer[:last_safe_end + 1]
                    else:
                        current_fragment = fragment_buffer

                    if "last_fragment" not in globals():
                        globals()["last_fragment"] = ""

                    if current_fragment != globals()["last_fragment"]:
                        globals()["last_fragment"] = current_fragment
                        yield f"### 🧠 Answer\n\n{answer}", sources_text




                elif data.get("type") == "sources":
                    sources = data["content"]
                    if sources:
                        urls = list({s.get("url", "") for s in sources if s.get("url")})
                        sources_text = "### 🔗 Sources\n" + "\n".join([f"- {u}" for u in urls])
                    else:
                        sources_text = "### 🔗 Sources\nNo sources available"

                elif data.get("type") == "error":
                    answer += f"\n[Error: {data['content']}]"
                    yield f"### 🧠 Answer\n\n{answer}", sources_text

                elif data.get("type") == "done":
                    # Final update
                    yield f"### 🧠 Answer\n\n{answer}", sources_text
                    return

        except Exception as e:
            yield f"[Streaming Error: {str(e)}]", ""

    # =========================
    # NON-STREAMING
    # =========================
    else:
        try:
            response = requests.post(
                f"{API_URL}/chat",
                json={"query": query, "top_k": 5, "use_llm": False},
                
                timeout=300
            )
            response.raise_for_status()
            data = response.json()

            answer = data.get("answer", "No answer received")
            sources = data.get("sources", [])
            if sources:
                urls = list({s.get("url", "") for s in sources if s.get("url")})
                sources_text = "### 🔗 Sources\n" + "\n".join([f"- {u}" for u in urls])
            else:
                sources_text = "### 🔗 Sources\nNo sources available"

            if data.get("llm_error"):
                answer += f"\n\n[Note: LLM generation failed, using fallback. Error: {data['llm_error']}]"

            yield f"### 🧠 Answer\n\n{answer}", sources_text

        except Exception as e:
            yield f"[Error: {str(e)}]", ""


def create_interface():
    """Create and return Gradio interface."""
    with gr.Blocks(title="💬 RAG Chatbot", theme=gr.themes.Soft()) as demo:

        gr.Markdown("""
        <div style="text-align:center">
            <h1 style="color:#4B9CD3;">💬 RAG Chatbot</h1>
            <p>Ask questions and get real-time answers with source citations.</p>
        </div>
        """)

        with gr.Row():
            with gr.Column(scale=1):
                query_input = gr.Textbox(
                    label="🔍 Ask your question",
                    placeholder="e.g., What is this website about?",
                    lines=3
                )
                with gr.Row():
                    use_llm_checkbox = gr.Checkbox(label="Use local LLM", value=False)
                    use_streaming_checkbox = gr.Checkbox(label="Enable streaming", value=True)
                submit_btn = gr.Button("🚀 Ask", variant="primary")

            with gr.Column(scale=2):
                answer_output = gr.Markdown(label="🧠 Answer")
                sources_output = gr.Markdown(label="🔗 Sources")

        # 1) Reset outputs first (fixes empty answer issue)
        submit_btn.click(
            fn=lambda q, s: ("", ""),
            inputs=[query_input, use_streaming_checkbox],
            outputs=[answer_output, sources_output]
        )

        # 2) Then run the actual chatbot
        submit_btn.click(
            fn=query_chatbot_streaming,
            inputs=[query_input, use_streaming_checkbox, use_llm_checkbox],
            outputs=[answer_output, sources_output]
        )

        gr.Markdown("""
        ---
        ### 💡 Example Queries:
        - 💌 Give me quotes about **love**
        - 💪 Show me quotes about **motivation**
        - 😂 Share some **funny quotes**
        - 🌟 What are the quotes about **success**?
        - 🎯 Top quotes about **life goals**
        - Summarize all the quotes from Marilyn Monroe found on the site.
        - What is the saddest quote you can find? Explain why it is sad.
        - If Albert Einstein and Marilyn Monroe had a conversation about success, what would they say to each other based on their quotes?
        - What is the main theme of the "inspirational" quotes? Give me a short summary.
         
        """)


    return demo


if __name__ == "__main__":
    print(f"Starting Gradio app. API URL: {API_URL}")
    demo = create_interface()
    demo.launch(server_name="0.0.0.0", server_port=7777, share=True)
