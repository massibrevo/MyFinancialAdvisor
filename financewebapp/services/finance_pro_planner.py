import pandas as pd
import streamlit as st

from financewebapp.calculations import HousingScenario, monthly_payment, project_housing
from financewebapp.ui import chart, euro, page_heading, results_table, save_summary

RENT = "Patrimonio in affitto"
BUY = "Patrimonio acquistando"
EQUITY = "Valore netto dell’immobile"
REAL_RENT = "Affitto in euro di oggi"
REAL_BUY = "Acquisto in euro di oggi"


def show_finance_pro_planner() -> None:
    page_heading(
        "Casa o affitto",
        "Confronta il patrimonio netto di chi compra casa e di chi resta in affitto, "
        "partendo dallo stesso capitale e dallo stesso budget mensile.",
    )
    controls, results = st.columns([1, 2], gap="large")
    with controls, st.container(border=True):
        st.subheader("Ipotesi", anchor=False)
        years = st.slider("Orizzonte (anni)", 1, 50, 25)
        savings = st.number_input("Capitale iniziale (€)", 0, 100_000_000, 100_000, step=1_000)
        budget = st.number_input("Budget mensile prima dell’abitazione (€)", 0, 1_000_000, 2_200, step=100)
        rent = st.number_input("Affitto mensile (€)", 0, 1_000_000, 1_100, step=50)
        price = st.number_input("Prezzo dell’immobile (€)", 1, 100_000_000, 350_000, step=5_000)
        with st.expander("Finanziamento e rendimenti"):
            down_payment = st.slider("Anticipo (%)", 0, 100, 20)
            purchase_cost = st.slider("Spese d’acquisto (%)", 0.0, 20.0, 5.0, 0.5)
            mortgage_rate = st.slider("Tasso fisso del mutuo (%)", 0.0, 20.0, 3.5, 0.1)
            mortgage_years = st.slider("Durata del mutuo (anni)", 1, 40, 25)
            maintenance = st.number_input("Spese mensili di proprietà (€)", 0, 1_000_000, 200, step=50)
            investment_growth = st.slider("Rendimento dell’investimento (%)", -10.0, 20.0, 4.0, 0.1)
            property_growth = st.slider("Crescita del valore della casa (%)", -10.0, 15.0, 2.0, 0.1)
            inflation = st.slider("Inflazione annua (%)", 0.0, 15.0, 2.0, 0.1)

    scenario = HousingScenario(
        years=years, savings=savings, budget=budget, rent=rent, price=price,
        down_payment_percent=down_payment, purchase_cost_percent=purchase_cost,
        maintenance=maintenance, mortgage_rate=mortgage_rate, mortgage_years=mortgage_years,
        investment_growth=investment_growth, property_growth=property_growth, inflation=inflation,
    )
    with results:
        payment = monthly_payment(scenario.mortgage, mortgage_rate, mortgage_years * 12)
        try:
            rows = project_housing(scenario)
        except ValueError as error:
            st.session_state.get("simulation_summaries", {}).pop("Casa o affitto", None)
            st.warning(str(error))
            st.caption(f"Capitale necessario {euro(scenario.upfront_cost)}. Spesa abitativa "
                       f"mensile da coprire {euro(max(rent, payment + maintenance))}.")
            return

        end = rows[-1]
        st.caption(f"Anticipo e spese {euro(scenario.upfront_cost)} · Rata mutuo {euro(payment)}/mese")
        nominal = st.segmented_control(
            "Valuta dei risultati", ["Nominale", "Euro di oggi"],
            default="Nominale", selection_mode="single", required=True,
        ) == "Nominale"
        values = (
            (end.rent_net_worth, end.buy_net_worth) if nominal else (end.rent_real, end.buy_real)
        )
        rent_metric, buy_metric, difference_metric = st.columns(3)
        rent_metric.metric("Affitto", euro(values[0]), border=True)
        buy_metric.metric("Acquisto", euro(values[1]), border=True)
        difference_metric.metric("Acquisto − affitto", euro(values[1] - values[0]), border=True)
        frame = pd.DataFrame({
            "Anno": [row.year for row in rows],
            RENT: [row.rent_net_worth for row in rows],
            BUY: [row.buy_net_worth for row in rows],
            EQUITY: [row.buy_home_equity for row in rows],
            REAL_RENT: [row.rent_real for row in rows],
            REAL_BUY: [row.buy_real for row in rows],
        })
        chart(frame, "Anno", (RENT, BUY) if nominal else (REAL_RENT, REAL_BUY),
              title="Patrimonio netto nel tempo")
        with st.expander("Dati ed esportazione"):
            results_table(frame, "casa-o-affitto")
        with st.expander("Come funziona il confronto"):
            st.write(
                "Ogni mese, entrambi gli scenari investono ciò che resta del budget dopo "
                "le spese abitative. Nel caso dell’acquisto, il patrimonio include il "
                "valore della casa meno il debito residuo. Affitto e spese mensili di proprietà "
                "restano fissi. I risultati ignorano costi di vendita e imposte sui rendimenti."
            )
        save_summary("Casa o affitto", (
            f"Orizzonte {years} anni. Patrimonio nominale in affitto {euro(end.rent_net_worth)}, "
            f"acquistando {euro(end.buy_net_worth)}. Rendimento annuo {investment_growth}%, "
            f"crescita immobile {property_growth}%, inflazione {inflation}%. "
            "Stesso capitale e stesso budget mensile, canone e spese di proprietà fissi."
        ))
