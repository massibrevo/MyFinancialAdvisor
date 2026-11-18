"""OpenAI Responses API adapter, independent of Streamlit."""

from collections.abc import Iterator

from openai import OpenAI

DEFAULT_MODEL = "gpt-6.2-sol"
INSTRUCTIONS = """Sei l'assistente di MyFinancialAdvisor. Rispondi nella lingua dell'utente.
Spiega concetti di finanza personale e interpreta le simulazioni fornite in modo educativo.
Distingui dati, ipotesi e risultati. Evidenzia le variabili che possono cambiare la conclusione.
Per i numeri delle simulazioni usa i risultati forniti dall'app senza inventare valori.
Non offrire raccomandazioni personalizzate, promesse di rendimento o dati di mercato in tempo
reale. Non chiedere credenziali, identificativi o documenti finanziari. Usa un linguaggio
chiaro, indica l'incertezza e invita a verificare i casi che dipendono da norme o contratti.
"""


class IncompleteResponse(RuntimeError):
    """The stream ended without completing the response."""


def stream_answer(
    client: OpenAI, model: str, messages: list[dict[str, str]], summaries: str = ""
) -> Iterator[str]:
    instructions = INSTRUCTIONS
    if summaries:
        instructions += "\nRiepiloghi delle simulazioni inclusi dall'utente:\n" + summaries
    options = {"reasoning": {"effort": "low"}} if model == DEFAULT_MODEL else {}
    with client.responses.create(
        model=model,
        instructions=instructions,
        input=messages[-12:],
        max_output_tokens=2400,
        store=False,
        stream=True,
        **options,
    ) as response:
        for event in response:
            if event.type in {"response.output_text.delta", "response.refusal.delta"}:
                yield event.delta
            elif event.type == "response.completed":
                return
            elif event.type in {"error", "response.failed", "response.incomplete"}:
                raise IncompleteResponse()
    raise IncompleteResponse()
