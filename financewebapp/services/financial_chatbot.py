import os

import streamlit as st
from openai import APIConnectionError, APIError, AuthenticationError, OpenAI, RateLimitError

from financewebapp.assistant import DEFAULT_MODEL, IncompleteResponse, stream_answer
from financewebapp.ui import page_heading


def show_financial_chatbot() -> None:
    page_heading(
        "Assistente AI",
        "Chiedi come leggere un risultato o quali ipotesi cambiare per esplorare un altro scenario.",
    )
    model = os.getenv("OPENAI_MODEL", "").strip() or DEFAULT_MODEL
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    with st.expander("Connessione e privacy", expanded=not api_key):
        st.caption(
            f"Modello attivo: `{model}`. Quando invii un messaggio, l’app trasmette a OpenAI "
            "la domanda, la cronologia recente e i riepiloghi che scegli di includere."
        )
        if not api_key:
            api_key = st.text_input("Chiave API OpenAI", type="password", key="openai_session_key").strip()
        st.caption("Usa dati di esempio o aggregati. Evita identificativi, password e documenti personali.")

    messages = st.session_state.setdefault("assistant_messages", [])
    controls, reset = st.columns([3, 1])
    summaries = st.session_state.get("simulation_summaries", {})
    selection = controls.multiselect("Riepiloghi da condividere con OpenAI", list(summaries))
    if selection:
        with st.expander("Anteprima dei dati condivisi"):
            for page_name in selection:
                st.write(summaries[page_name])
    if reset.button("Nuova chat", icon=":material/restart_alt:", disabled=not messages):
        messages.clear()

    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if not api_key:
        st.info("Inserisci una chiave API per attivare la chat. I simulatori funzionano senza chiave.")
    elif not messages:
        st.caption("Per iniziare, prova a chiedere come l’inflazione cambia il capitale reale.")

    prompt = st.chat_input("Scrivi una domanda…", disabled=not api_key, max_chars=2400)
    if not prompt or not prompt.strip():
        return

    user_message = {"role": "user", "content": prompt.strip()}
    with st.chat_message("user"):
        st.markdown(user_message["content"])

    context = "\n".join(summaries[name] for name in selection)
    with st.chat_message("assistant"):
        try:
            with OpenAI(api_key=api_key, timeout=45.0, max_retries=1) as client:
                answer = st.write_stream(stream_answer(client, model, [*messages, user_message], context))
        except AuthenticationError:
            st.error("OpenAI ha rifiutato la chiave API. Verifica la chiave e riprova.")
            return
        except RateLimitError:
            st.error("Limite API raggiunto. Controlla la quota del progetto o riprova tra poco.")
            return
        except APIConnectionError:
            st.error("Connessione a OpenAI interrotta. Riprova tra poco.")
            return
        except (APIError, IncompleteResponse):
            st.error("La risposta non è stata completata. Verifica l’accesso al modello o riprova.")
            return

        if not isinstance(answer, str) or not answer.strip():
            st.warning("Il modello non ha restituito testo. Prova a riformulare la domanda.")
            return
    messages.extend([user_message, {"role": "assistant", "content": answer}])
    del messages[:-12]
