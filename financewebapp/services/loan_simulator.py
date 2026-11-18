import pandas as pd
import streamlit as st

from financewebapp.calculations import amortize, monthly_payment
from financewebapp.ui import chart, euro, page_heading, results_table, save_summary

BALANCE = "Debito residuo"
INTEREST = "Interessi cumulati"


def show_loan_simulation() -> None:
    page_heading(
        "Prestiti e mutui",
        "Simula un finanziamento a tasso fisso e misura quanto tempo e interessi "
        "puoi risparmiare con un versamento extra.",
    )
    controls, results = st.columns([1, 2], gap="large")
    with controls, st.container(border=True):
        st.subheader("Finanziamento", anchor=False)
        principal = st.number_input("Importo (€)", 1.0, 100_000_000.0, 100_000.0, step=1_000.0)
        rate = st.slider("Tasso nominale annuo (%)", 0.0, 25.0, 5.0, 0.1)
        years = st.slider("Durata (anni)", 1, 40, 15)
        extra = st.number_input("Versamento extra mensile (€)", 0.0, 100_000_000.0, 0.0, step=50.0)

    months = years * 12
    baseline = amortize(principal, rate, months)
    rows = amortize(principal, rate, months, extra) if extra else baseline
    interest = rows[-1].cumulative_interest
    interest_saved = baseline[-1].cumulative_interest - interest
    months_saved = months - len(rows)
    payment = monthly_payment(principal, rate, months)
    with results:
        regular, total, payoff = st.columns(3)
        regular.metric("Rata base", euro(payment), border=True)
        total.metric("Interessi totali", euro(interest), border=True)
        payoff.metric("Estinzione", f"{len(rows)} mesi", border=True)
        st.caption(f"Con l’extra risparmi {euro(interest_saved)} di interessi e {months_saved} mesi. "
                   f"Totale pagato {euro(principal + interest)}.")
        frame = pd.DataFrame({
            "Mese": [row.month for row in rows],
            "Rata effettiva": [row.payment for row in rows],
            "Quota capitale": [row.principal for row in rows],
            "Quota interessi": [row.interest for row in rows],
            BALANCE: [row.balance for row in rows],
            INTEREST: [row.cumulative_interest for row in rows],
        })
        comparison = pd.DataFrame({
            "Mese": range(months + 1),
            BALANCE: [principal, *(row.balance for row in rows), *([0] * months_saved)],
            "Senza versamento extra": [principal, *(row.balance for row in baseline)],
        })
        series = (BALANCE, "Senza versamento extra") if extra else (BALANCE,)
        chart(comparison, "Mese", series, title="Andamento del debito residuo")
        with st.expander("Piano di ammortamento ed esportazione"):
            results_table(frame, "piano-ammortamento")
        with st.expander("Come funziona il calcolo"):
            st.write(
                "Il tasso mensile è il tasso nominale annuo diviso per dodici. L’extra mensile "
                "riduce subito il capitale e l’ultima rata è limitata al debito residuo più "
                "gli interessi del mese. Il calcolo esclude spese accessorie e penali."
            )
        save_summary("Prestiti e mutui", (
            f"Prestito di {euro(principal)} a tasso fisso {rate}%, durata iniziale {months} mesi. "
            f"Rata base {euro(payment)}, extra mensile {euro(extra)}. Estinzione in {len(rows)} mesi, "
            f"interessi {euro(interest)} e risparmio {euro(interest_saved)} rispetto al piano base."
        ))
