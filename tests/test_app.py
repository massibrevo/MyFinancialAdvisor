import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


def open_page(module, name):
    return AppTest.from_string(
        f"from financewebapp.services.{module} import {name}\n{name}()",
        default_timeout=25,
    ).run()


class DashboardTests(unittest.TestCase):
    def test_overview_links_to_all_four_tools(self):
        entry_point = Path(__file__).resolve().parents[1] / "main.py"
        app = AppTest.from_file(entry_point, default_timeout=25).run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get("page_link")), 4)

    def test_housing_can_display_real_values_and_export(self):
        app = open_page("finance_pro_planner", "show_finance_pro_planner")
        self.assertFalse(app.exception)
        self.assertEqual(len(app.metric), 3)
        nominal = app.metric[0].value
        app.segmented_control[0].set_value("Euro di oggi").run()
        self.assertFalse(app.exception)
        self.assertNotEqual(app.metric[0].value, nominal)
        self.assertEqual(app.get("download_button")[0].proto.label, "Scarica Excel")

    def test_loan_page_supports_zero_interest(self):
        app = open_page("loan_simulator", "show_loan_simulation")
        app.slider[0].set_value(0.0).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[1].value, "€ 0")

    def test_retirement_page_supports_no_monthly_withdrawal(self):
        app = open_page("retirement_simulator", "show_retirement_simulation")
        app.number_input[4].set_value(0).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[2].value, "Nessun prelievo")

    def test_assistant_is_optional_without_a_key(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}):
            app = open_page("financial_chatbot", "show_financial_chatbot")
        self.assertFalse(app.exception)
        self.assertTrue(app.chat_input[0].proto.disabled)

    def test_assistant_streams_and_sends_only_selected_summaries(self):
        with (
            patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}),
            patch("financewebapp.services.financial_chatbot.OpenAI"),
            patch("financewebapp.services.financial_chatbot.stream_answer") as stream,
        ):
            stream.return_value = iter(["Capitale ", "reale."])
            app = AppTest.from_string(
                'import streamlit as st\n'
                'from financewebapp.services.financial_chatbot import show_financial_chatbot\n'
                'st.session_state["simulation_summaries"] = '
                '{"Pensione": "Scenario scelto", "Mutuo": "Scenario privato"}\n'
                'show_financial_chatbot()',
                default_timeout=25,
            ).run()
            app.multiselect[0].select("Pensione").run()
            app.chat_input[0].set_value("Come leggo il risultato?").run()
        self.assertFalse(app.exception)
        self.assertEqual(stream.call_args.args[-1], "Scenario scelto")
        self.assertEqual(app.session_state["assistant_messages"][-1]["content"], "Capitale reale.")
