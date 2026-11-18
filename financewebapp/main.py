from pathlib import Path

import streamlit as st

from financewebapp.services.finance_pro_planner import show_finance_pro_planner
from financewebapp.services.financial_chatbot import show_financial_chatbot
from financewebapp.services.landing_page import show_landing_page
from financewebapp.services.loan_simulator import show_loan_simulation
from financewebapp.services.retirement_simulator import show_retirement_simulation

STYLE = Path(__file__).with_name("styles.css")


def main() -> None:
    st.set_page_config(
        page_title="MyFinancialAdvisor",
        page_icon=":material/monitoring:",
        layout="wide",
        initial_sidebar_state="auto",
    )
    st.html(STYLE)

    tools = [
        (show_finance_pro_planner, "Casa o affitto", "casa",
         "Confronta le due alternative sullo stesso orizzonte.", ":material/home_work:"),
        (show_loan_simulation, "Prestiti e mutui", "prestiti",
         "Calcola la rata e l’effetto di un versamento extra.", ":material/payments:"),
        (show_retirement_simulation, "Pensione", "pensione",
         "Stima il capitale futuro e il suo potere d’acquisto.", ":material/savings:"),
        (show_financial_chatbot, "Assistente AI", "assistente",
         "Esplora le ipotesi o chiedi come interpretare i risultati.", ":material/auto_awesome:"),
    ]
    pages = [
        (st.Page(view, title=title, url_path=path, icon=icon), title, description, icon)
        for view, title, path, description, icon in tools
    ]

    def overview() -> None:
        show_landing_page(pages)

    home = st.Page(overview, title="Panoramica", icon=":material/space_dashboard:", default=True)
    current = st.navigation([home, *(page for page, *_ in pages)])
    current.run()


if __name__ == "__main__":
    main()
