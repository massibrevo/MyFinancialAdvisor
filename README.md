# MyFinancialAdvisor 2.0

MyFinancialAdvisor è una dashboard in italiano per confrontare scenari finanziari in euro. I risultati si aggiornano quando cambi le ipotesi e puoi scaricare i dati di ciascun simulatore in Excel.

| Strumento | Risultato |
| --- | --- |
| **Casa o affitto** | Patrimonio netto a parità di capitale e budget, in euro nominali o di oggi |
| **Prestiti e mutui** | Piano di ammortamento, interessi e mesi risparmiati con un extra mensile |
| **Pensione** | Capitale nominale e reale, versamenti e anni di spese coperte |
| **Assistente AI** | Spiegazioni in chat con riepiloghi dei simulatori condivisi su scelta dell’utente |

I simulatori hanno finalità informative. Le ipotesi di esempio servono per esplorare il funzionamento del modello.

## Avvio locale

Usa Python 3.11 o superiore. La procedura qui sotto è stata verificata con Python 3.11.

```bash
git clone https://github.com/massibrevo/MyFinancialAdvisor.git
cd MyFinancialAdvisor
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run main.py
```

Apri [localhost:8501](http://localhost:8501). Su Windows PowerShell, attiva l’ambiente con `.venv\Scripts\Activate.ps1`.

## Assistente AI

I simulatori funzionano anche senza un account OpenAI. Per attivare la chat, inserisci una chiave API nella schermata **Assistente AI** oppure configura `OPENAI_API_KEY` nelle variabili d’ambiente del processo. `OPENAI_MODEL` permette di sostituire `gpt-6.2-sol` con un modello compatibile con la Responses API disponibile sul tuo progetto. [Catalogo OpenAI](https://developers.openai.com/api/docs/models/gpt-6.2-sol)

La chiave inserita nell’interfaccia appartiene alla sessione Streamlit. Una chiave impostata lato server può essere usata da chiunque acceda all’app, quindi usala soltanto per un’istanza privata o con accesso controllato.

La chat trasmette a OpenAI la domanda e la cronologia recente. Puoi aggiungere i riepiloghi selezionando le singole simulazioni e controllando l’anteprima. L’app invia le richieste con `store=False`. Il pulsante **Nuova chat** svuota la conversazione in memoria. [Controlli sui dati OpenAI](https://developers.openai.com/api/docs/guides/your-data)

## Manutenzione

- `main.py` avvia l’app e `financewebapp/main.py` definisce la navigazione.
- `financewebapp/calculations.py` contiene i calcoli indipendenti da Streamlit.
- `financewebapp/services/` contiene le schermate. `financewebapp/ui.py` condivide grafici, tabelle ed esportazione.
- `financewebapp/assistant.py` gestisce lo streaming della Responses API.
- `requirements.in` dichiara i requisiti. `requirements.txt` fissa anche le dipendenze transitive.

```bash
python -m unittest discover -s tests -v
python -m pip check
uv pip compile requirements.in --python-version 3.11 --universal -o requirements.txt
```

Per aggiornare le dipendenze transitive durante la ricompilazione aggiungi `--upgrade`. I test dell’assistente simulano le risposte del provider e non richiedono una chiave.

[Metodologia e limiti dei simulatori](docs/metodologia.md)
