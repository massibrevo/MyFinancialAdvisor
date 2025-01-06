import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def calculate_invested_savings(current_age, target_age, initial_savings, monthly_contribution, annual_lump_sum, annual_return, tax_rate):
    """Calculate annual invested savings including monthly contributions and an annual lump sum."""
    years_to_invest = target_age - current_age
    total_months = years_to_invest * 12
    monthly_rate = (annual_return * (1 - tax_rate / 100)) / 12 / 100

    invested_savings = [initial_savings]

    for month in range(1, total_months + 1):
        updated_savings = invested_savings[-1] * (1 + monthly_rate) + monthly_contribution
        if month % 12 == 0:  # Add lump sum at the end of each year
            updated_savings += annual_lump_sum
        invested_savings.append(updated_savings)

    # Keep only annual snapshots
    invested_savings_annual = [invested_savings[i * 12] for i in range(years_to_invest + 1)]
    return invested_savings_annual


def calculate_non_invested_savings(current_age, target_age, initial_savings, monthly_contribution, annual_lump_sum):
    """Calculate annual non-invested savings."""
    years_to_invest = target_age - current_age
    non_invested_savings = [initial_savings]

    for year in range(1, years_to_invest + 1):
        total = non_invested_savings[-1] + monthly_contribution * 12 + annual_lump_sum
        non_invested_savings.append(total)

    return non_invested_savings


def calculate_real_savings(invested_savings, current_age, target_age, inflation_rate):
    """Calculate inflation-adjusted ('real') savings."""
    real_savings = []
    for idx, saving in enumerate(invested_savings):
        real_value = saving / ((1 + inflation_rate / 100) ** idx)
        real_savings.append(real_value)
    return real_savings


def show_retirement_simulation():
    st.title("Retirement Simulator")
    st.write("Visualize your retirement savings growth and how long your savings will last.")

    # --- Assumptions Section ---
    st.markdown("### Assumptions for Calculation")
    st.markdown("""
    - **Taxes:** Taxes apply to annual investment returns.
    - **Inflation:** Adjusts savings for purchasing power.
    - **Expenses:** Calculates how long savings last during retirement.
    """)

    # --- Inputs ---
    current_age = st.number_input("Current Age", min_value=18, max_value=80, value=30)
    target_age = st.number_input("Target Retirement Age", min_value=current_age + 1, max_value=100, value=65)
    initial_savings = st.number_input("Initial Savings (€)", min_value=0.0, value=10000.0)
    annual_lump_sum = st.number_input("Annual Lump Sum Contribution (€)", min_value=0.0, value=0.0)
    monthly_contribution = st.number_input("Monthly Contribution (€)", min_value=0.0, value=1000.0)

    financial_product = st.selectbox(
        "Select Financial Product",
        options=["ETF", "Aggressive Stocks", "Bonds", "Deposit Accounts"],
        index=0
    )
    product_return_estimates = {
        "ETF": 6.0,
        "Aggressive Stocks": 10.0,
        "Bonds": 3.0,
        "Deposit Accounts": 1.5,
    }
    default_return = product_return_estimates[financial_product]
    annual_return = st.slider("Expected Annual Return (%)", min_value=0.0, max_value=15.0, value=default_return)
    inflation_rate = st.slider("Inflation Rate (% per year)", min_value=0.0, max_value=10.0, value=2.0)
    tax_rate = st.slider("Tax Rate on Investment Returns (%)", min_value=0.0, max_value=50.0, value=15.0)
    monthly_expenses = st.number_input("Estimated Monthly Retirement Expenses (€)", min_value=0.0, value=2000.0)

    # Validation
    if current_age <= 0 or target_age <= 0 or initial_savings < 0 or monthly_contribution < 0:
        st.error("Invalid input! Please ensure all values are non-negative and logical.")
        return

    # --- Calculations ---
    invested_savings = calculate_invested_savings(
        current_age, target_age, initial_savings, monthly_contribution, annual_lump_sum, annual_return, tax_rate
    )
    non_invested_savings = calculate_non_invested_savings(
        current_age, target_age, initial_savings, monthly_contribution, annual_lump_sum
    )
    real_savings = calculate_real_savings(invested_savings, current_age, target_age, inflation_rate)

    # Calculate how many years savings will last
    total_savings_at_retirement = invested_savings[-1]
    annual_expenses = monthly_expenses * 12
    years_savings_will_last = total_savings_at_retirement / annual_expenses

    # --- Visualization ---
    years_list = list(range(current_age, target_age + 1))
    fig = go.Figure()

    # Invested Savings
    fig.add_trace(go.Scatter(
        x=years_list,
        y=invested_savings,
        mode='lines+markers',
        name=f"Invested Savings (Lasts ~{years_savings_will_last:.1f} yrs)",
        line=dict(color='purple')
    ))

    # Non-Invested Savings
    fig.add_trace(go.Scatter(
        x=years_list,
        y=non_invested_savings,
        mode='lines+markers',
        name="Non-Invested Savings",
        line=dict(dash='dot', color='blue')
    ))

    # Inflation-Adjusted Savings
    fig.add_trace(go.Scatter(
        x=years_list,
        y=real_savings,
        mode='lines',
        name="Real Savings (Inflation Adjusted)",
        line=dict(dash='dash', color='green')
    ))

    fig.update_layout(
        title="Retirement Savings Growth",
        xaxis_title="Age",
        yaxis_title="€ Savings",
        template="plotly_white"
    )

    st.plotly_chart(fig)

    # --- Summary Table ---
    summary_data = {
        "Age": years_list,
        "Invested Savings (€)": invested_savings,
        "Non-Invested Savings (€)": non_invested_savings,
        "Real Savings (Inflation Adjusted)": real_savings
    }
    df = pd.DataFrame(summary_data)
    st.dataframe(df.style.format("{:,.2f}"))

    # --- Savings Duration ---
    st.subheader("How Long Will My Savings Last?")
    st.write(
        f"Your savings will last approximately **{years_savings_will_last:.1f} years** "
        f"after retirement, based on your estimated expenses of €{monthly_expenses:,.2f} per month."
    )

    # --- Disclaimer ---
    st.write("---")
    st.caption(
        "Disclaimer: This tool is for simulation purposes only and should not be considered financial advice. "
        "Always consult a certified financial advisor before making decisions."
    )
