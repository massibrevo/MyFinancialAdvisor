import pandas as pd
import streamlit as st

from financewebapp.calculations import project_retirement
from financewebapp.ui import chart, euro, page_heading, results_table, save_summary

INVESTED = "Capitale nominale"
CONTRIBUTED = "Capitale versato"
REAL = "Capitale in euro di oggi"


def show_retirement_simulation() -> None:
    page_heading(
        "Pensione",
        "Proietta i tuoi risparmi, osserva l’effetto di rendimento e inflazione "
        "e stima quanti anni di spese potresti coprire.",
    )
    controls, results = st.columns([1, 2], gap="large")
    with controls, st.container(border=True):
        st.subheader("Accumulo", anchor=False)
        ages = st.columns(2)
        age = ages[0].number_input("Età attuale", 18, 99, 30)
        target_age = ages[1].number_input("Età alla pensione", 19, 100, 65)
        initial = st.number_input("Capitale iniziale (€)", 0, 100_000_000, 10_000, step=1_000)
        monthly = st.number_input("Versamento mensile (€)", 0, 1_000_000, 1_000, step=100)
        expenses = st.number_input("Prelievo mensile in euro di oggi", 0, 1_000_000, 2_000, step=100)
        with st.expander("Rendimenti e versamenti extra"):
            annual = st.number_input("Versamento a fine anno (€)", 0, 10_000_000, 0, step=500)
            annual_return = st.slider("Rendimento annuo lordo (%)", -10.0, 20.0, 6.0, 0.1)
            tax = st.slider("Tassazione sul rendimento positivo (%)", 0.0, 60.0, 15.0, 0.5)
            inflation = st.slider("Inflazione annua (%)", 0.0, 15.0, 2.0, 0.1)

    with results:
        try:
            rows = project_retirement(age, target_age, initial, monthly, annual, annual_return, tax, inflation)
        except ValueError as error:
            st.session_state.get("simulation_summaries", {}).pop("Pensione", None)
            st.warning(str(error))
            return
        end = rows[-1]
        runway = f"{end.real / (expenses * 12):.1f} anni".replace(".", ",") if expenses else "Nessun prelievo"
        real, nominal, duration = st.columns(3)
        real.metric("In euro di oggi", euro(end.real), border=True)
        nominal.metric("Capitale nominale", euro(end.invested), border=True)
        duration.metric("Copertura stimata", runway, border=True)
        frame = pd.DataFrame({
            "Età": [row.age for row in rows],
            INVESTED: [row.invested for row in rows],
            CONTRIBUTED: [row.contributed for row in rows],
            REAL: [row.real for row in rows],
        })
        chart(frame, "Età", (INVESTED, REAL, CONTRIBUTED), title="Capitale fino alla pensione")
        with st.expander("Proiezione annuale ed esportazione"):
            results_table(frame, "proiezione-pensione")
        with st.expander("Come funziona la stima"):
            st.write(
                "La tassazione è un’aliquota ipotetica sul rendimento positivo. Il rendimento "
                "netto viene capitalizzato mensilmente. La copertura divide il capitale reale "
                "per i prelievi annui reali e assume rendimento reale nullo dopo il pensionamento."
            )
        save_summary("Pensione", (
            f"Età attuale {age}, pensionamento a {target_age} anni. Capitale nominale "
            f"{euro(end.invested)}, capitale in euro di oggi {euro(end.real)}. "
            f"Prelievo mensile {euro(expenses)}, copertura stimata {runway}. "
            f"Rendimento lordo annuo {annual_return}%, inflazione annua {inflation}%."
        ))
