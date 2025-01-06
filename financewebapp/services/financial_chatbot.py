import streamlit as st
import threading
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer

# ------------------
# 1. Model Loading
# ------------------
@st.cache_resource
def load_model():
    """
    Loads the model and tokenizer once and caches them.
    """
    model_name = "EleutherAI/gpt-neo-1.3B"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    return model, tokenizer

# ---------------------------
# 2. Streaming Generate Logic
# ---------------------------
def generate_stream(
    prompt: str, 
    model, 
    tokenizer, 
    max_new_tokens: int = 150
):
    """
    Generates text from the model token-by-token using TextIteratorStreamer.
    Yields partial text as it is generated.
    """
    # Create a streamer that yields new tokens one at a time.
    streamer = TextIteratorStreamer(
        tokenizer, 
        skip_prompt=True, 
        skip_special_tokens=True
    )

    # Prepare the input tensor.
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(model.device)

    # Define the generation in a thread so we can iterate over tokens in the main thread.
    def threaded_generation():
        model.generate(
            input_ids=input_ids,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            streamer=streamer
        )

    # Run generation in a separate thread.
    thread = threading.Thread(target=threaded_generation)
    thread.start()

    # Collect tokens as they stream in, building partial_text gradually.
    partial_text = ""
    for new_text in streamer:
        partial_text += new_text
        yield partial_text

    # Ensure the generation thread finishes.
    thread.join()


# -----------------------
# 3. Financial Chatbot UI
# -----------------------
def show_financial_chatbot():
    st.title("💬 Financial Chatbot")
    st.write("Ask any financial-related question, and our chatbot will assist you.")

    # Initialize or retrieve session state
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "question_count" not in st.session_state:
        st.session_state.question_count = 0

    # 3a. Apply some custom CSS to mimic ChatGPT’s style
    st.markdown(
        """
        <style>
        .chat-container {
            max-height: 500px;
            overflow-y: auto;
            padding: 15px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background-color: #f9f9f9;
            margin-bottom: 20px;
        }
        .message {
            margin-bottom: 15px;
            padding: 12px;
            border-radius: 10px;
            display: inline-block;
            max-width: 75%;
            line-height: 1.4;
            font-size: 15px;
        }
        .user-message {
            background-color: #dcf2fa;
            color: #000;
            float: right;
            clear: both;
        }
        .assistant-message {
            background-color: #f3f3f3;
            color: #000;
            float: left;
            clear: both;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 3b. Display the conversation so far
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.conversation:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="message user-message">{msg["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="message assistant-message">{msg["content"]}</div>',
                unsafe_allow_html=True
            )
    st.markdown('</div>', unsafe_allow_html=True)

    # 3c. Input area to type the question
    user_input = st.text_area(
        label="", 
        placeholder="💬 Type your financial question here...", 
        height=80  # Must be >= 68
    )

    # 3d. "Send" button
    send_clicked = st.button("Send")
    if send_clicked:
        if not user_input.strip():
            st.warning("Please type a question before sending.")
        elif st.session_state.question_count >= 5:
            st.error("You have reached the maximum of 5 questions per session. Reset to start a new session.")
        else:
            # Record the user's message
            st.session_state.conversation.append({"role": "user", "content": user_input})
            st.session_state.question_count += 1

            # Partial streaming output
            with st.spinner("Generating response..."):
                model, tokenizer = load_model()
                placeholder = st.empty()  # We'll update this container as tokens arrive
                partial_text = ""

                for tokenized_text in generate_stream(user_input, model, tokenizer):
                    partial_text = tokenized_text
                    # Replace the placeholder content with the latest partial text
                    # (wrapped in assistant-message styling)
                    placeholder.markdown(
                        f'<div class="message assistant-message">{partial_text}</div>', 
                        unsafe_allow_html=True
                    )

                # Once generation is done, store the final partial_text in session
                st.session_state.conversation.append({"role": "assistant", "content": partial_text.strip()})

            # Force immediate UI refresh to show the complete conversation
            st.stop() # testing instead of st.experimental_rerun()

    # 3e. "Reset Chat" button
    reset_clicked = st.button("Reset Chat")
    if reset_clicked:
        st.session_state.conversation = []
        st.session_state.question_count = 0
        # IMPORTANT: Do NOT overwrite st.session_state.user_input here
        # Instead, we rely on st.experimental_rerun() to clear text_area next run
        st.stop() # testing instead of st.experimental_rerun()

    # 3f. Disclaimer
    st.markdown("---")
    st.caption(
        "**Disclaimer**: This chatbot provides general financial information and is "
        "not a substitute for professional financial advice. Always consult a "
        "certified financial advisor for guidance specific to your situation."
    )

# 4. Main entry point for Streamlit
def main():
    show_financial_chatbot()

if __name__ == "__main__":
    main()
