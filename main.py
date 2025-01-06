import streamlit as st
from financewebapp.services.landing_page import show_landing_page
from financewebapp.services.finance_pro_planner import show_finance_pro_planner
from financewebapp.services.retirement_simulator import show_retirement_simulation
from financewebapp.services.loan_simulator import show_loan_simulation
from financewebapp.services.financial_chatbot import show_financial_chatbot

# Custom styles for the light theme
def apply_custom_styles():
    st.markdown(
        """
        <style>
        /* Background color for the app */
        .main {
            background-color: #FFFFFF; /* White */
        }
        /* Sidebar background */
        .css-1d391kg {
            background-color: #F8F9FA !important; /* Light Grey */
        }
        /* Text color for titles and buttons */
        .stTitle, .stButton > button {
            color: #000000 !important; /* Black */
        }
        /* Primary button */
        .stButton > button {
            background-color: #007BFF; /* Blue */
            border: 1px solid #007BFF;
            border-radius: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Main function
def main():
    apply_custom_styles()  # Apply custom styles

    st.sidebar.title("Navigation")
    option = st.sidebar.radio(
        "Navigation", 
        ["Home", "Financial Services", "About Us"]
    )

    if option == "Home":
        show_landing_page()
    elif option == "Financial Services":
        # Wrap services in a dropdown menu
        service_option = st.sidebar.selectbox(
            "Select a Financial Service", 
            ["FinancePro Planner", "Retirement Simulator", "Loan Simulator", "Financial Chatbot"]
        )
        if service_option == "FinancePro Planner":
            show_finance_pro_planner()
        elif service_option == "Retirement Simulator":
            show_retirement_simulation()
        elif service_option == "Loan Simulator":
            show_loan_simulation()
        elif service_option == "Financial Chatbot":
            show_financial_chatbot()
    elif option == "About Us":
        show_about_us()

def show_about_us():
    st.title("About Us")
    st.markdown("""
    **Welcome to FinancePro Planner!**

    At **FinancePro Planner**, our mission is to empower individuals and businesses to achieve their financial goals. 
    With state-of-the-art tools, interactive simulations, and expert advice, we simplify complex financial decisions 
    and help you make data-driven choices.

    **What We Offer:**
    - Comprehensive financial planning tools.
    - Retirement savings simulations.
    - Advanced loan calculators.
    - An AI-powered financial chatbot for quick advice.

    **Our Vision:**
    To become the most trusted financial partner for individuals and businesses across the globe.

    **Contact Us:**
    - Email: support@financeproplanner.com
    - Phone: +1 234 567 890
    - Website: [www.financeproplanner.com](https://www.financeproplanner.com)

    Disclaimer: This application is for simulation purposes only and does not constitute financial advice. 
    Always consult with certified financial advisors for personalized guidance.
    """)

if __name__ == "__main__":
    main()
