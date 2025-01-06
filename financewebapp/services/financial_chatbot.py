import streamlit as st
import openai

# -------------------------------------
# 1. OpenAI Stream Helper Function
# -------------------------------------
def openai_stream(messages, model="gpt-3.5-turbo", temperature=0.7):
    """
    Calls the OpenAI ChatCompletion endpoint in streaming mode.
    Yields chunks of text as tokens are generated.
    """
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        stream=True
    )
    # Stream the response chunks
    for chunk in response:
        if "choices" in chunk:
            delta = chunk["choices"][0].get("delta", {})
            if "content" in delta:
                yield delta["content"]

# -------------------------------
# 2. Main Financial Chatbot Page
# -------------------------------
def show_financial_chatbot():
    st.title("💬 Financial Chatbot")
    st.write("Ask any financial-related question, and our chatbot will assist you.")

    # --- A) Check or get API key ---
    # If not stored in session, create a placeholder for it
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    # Ask user for the API key
    st.session_state.api_key = st.text_input(
        "Enter your OpenAI API Key:",
        value=st.session_state.api_key,
        type="password",  # Hide the input
    )
    # If no key, stop here
    if not st.session_state.api_key:
        st.warning("Please enter your OpenAI API key to continue.")
        return

    # Set the OpenAI key
    openai.api_key = st.session_state.api_key

    # --- B) Session Initialization ---
    if "conversation" not in st.session_state:
        # We'll store the conversation as a list of {"role": "...", "content": "..."}
        st.session_state.conversation = []
    if "question_count" not in st.session_state:
        st.session_state.question_count = 0

    # --- C) Chat Display CSS ---
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

    # --- D) Display the Conversation ---
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

    # --- E) User Input ---
    user_input = st.text_area(
        label="",
        placeholder="💬 Type your financial question here...",
        height=80  # must be >= 68
    )

    # --- F) "Send" Button ---
    send_clicked = st.button("Send")
    if send_clicked:
        if not user_input.strip():
            st.warning("Please type a question before sending.")
        elif st.session_state.question_count >= 5:
            st.error("You have reached the maximum of 5 questions per session. Reset to start a new session.")
        else:
            # 1) Add user message to conversation
            st.session_state.conversation.append({"role": "user", "content": user_input})
            st.session_state.question_count += 1

            # 2) Stream the response
            with st.spinner("Generating response..."):
                # Prepare a new list of messages for OpenAI: system + the entire conversation
                # Optionally, you can add a system message for context (like "You are a helpful financial expert...").
                openai_messages = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.conversation]

                # Placeholder for partial streaming
                placeholder = st.empty()
                partial_text = ""

                for chunk_text in openai_stream(openai_messages):
                    partial_text += chunk_text
                    # Update placeholder with the latest partial answer
                    placeholder.markdown(
                        f'<div class="message assistant-message">{partial_text}</div>',
                        unsafe_allow_html=True
                    )

                # Once complete, add the fully formed assistant message to the conversation
                st.session_state.conversation.append({"role": "assistant", "content": partial_text.strip()})

            # Force immediate UI update
            st.experimental_rerun()

    # --- G) "Reset Chat" Button ---
    reset_clicked = st.button("Reset Chat")
    if reset_clicked:
        st.session_state.conversation = []
        st.session_state.question_count = 0
        # We do NOT assign st.session_state.api_key = "" unless you want to forcibly clear user’s key
        # We'll just re-run the script so the user sees a fresh conversation
        st.experimental_rerun()

    # --- H) Disclaimer ---
    st.markdown("---")
    st.caption(
        "**Disclaimer**: This chatbot provides general financial information and is "
        "not a substitute for professional financial advice. Always consult a "
        "certified financial advisor for guidance specific to your situation."
    )


# 3. Main entry point
def main():
    show_financial_chatbot()

if __name__ == "__main__":
    main()
