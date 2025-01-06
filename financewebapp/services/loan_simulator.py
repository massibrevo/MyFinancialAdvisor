import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def calculate_loan_schedule(principal, annual_interest_rate, loan_term_years, monthly_extra_payment):
    """Calculate loan repayment schedule."""
    monthly_interest_rate = annual_interest_rate / 12 / 100
    total_months = loan_term_years * 12

    # Monthly payment calculation (Fixed Payment)
    monthly_payment = principal * (monthly_interest_rate * (1 + monthly_interest_rate) ** total_months) / (
            (1 + monthly_interest_rate) ** total_months - 1)

    schedule = []
    remaining_balance = principal
    total_interest_paid = 0

    for month in range(1, total_months + 1):
        interest_payment = remaining_balance * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment
        total_interest_paid += interest_payment
        remaining_balance -= principal_payment + monthly_extra_payment

        if remaining_balance < 0:
            remaining_balance = 0

        schedule.append({
            "Month": month,
            "Monthly Payment (€)": monthly_payment + monthly_extra_payment,
            "Principal Payment (€)": principal_payment + monthly_extra_payment,
            "Interest Payment (€)": interest_payment,
            "Remaining Balance (€)": remaining_balance,
            "Total Interest Paid (€)": total_interest_paid
        })

        if remaining_balance == 0:
            break

    return pd.DataFrame(schedule)


def create_loan_chart(schedule):
    """Create a plotly chart for the loan schedule."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=schedule["Month"],
        y=schedule["Remaining Balance (€)"],
        mode="lines",
        name="Remaining Balance",
        line=dict(color="blue")
    ))

    fig.add_trace(go.Scatter(
        x=schedule["Month"],
        y=schedule["Total Interest Paid (€)"],
        mode="lines",
        name="Total Interest Paid",
        line=dict(color="red", dash="dash")
    ))

    fig.update_layout(
        title="Loan Repayment Schedule",
        xaxis_title="Months",
        yaxis_title="Amount (€)",
        template="plotly_white",
    )

    return fig


def show_loan_simulation():
    """Display the Loan Simulation tool."""
    st.title("Loan Simulator")
    st.write("Simulate your loan repayment schedule and analyze the financial impact of additional payments.")

    # Inputs for loan parameters
    principal = st.number_input("Loan Amount (€)", min_value=0.0, value=100000.0, step=1000.0)
    annual_interest_rate = st.slider("Annual Interest Rate (%)", min_value=0.0, max_value=20.0, value=5.0, step=0.1)
    loan_term_years = st.slider("Loan Term (Years)", min_value=1, max_value=30, value=15, step=1)
    monthly_extra_payment = st.number_input("Monthly Extra Payment (€)", min_value=0.0, value=0.0, step=100.0)

    # Validate inputs
    if principal == 0 or loan_term_years == 0:
        st.warning("Please ensure all inputs are greater than 0.")
        return

    # Calculate loan schedule
    schedule = calculate_loan_schedule(principal, annual_interest_rate, loan_term_years, monthly_extra_payment)

    # Display chart
    fig = create_loan_chart(schedule)
    st.plotly_chart(fig)

    # Display summary
    total_months = schedule["Month"].iloc[-1]
    total_interest_paid = schedule["Total Interest Paid (€)"].iloc[-1]
    total_paid = schedule["Monthly Payment (€)"].sum()

    st.write("### Loan Summary")
    st.write(f"**Total Months to Repay:** {total_months}")
    st.write(f"**Total Interest Paid:** €{total_interest_paid:,.2f}")
    st.write(f"**Total Amount Paid:** €{total_paid:,.2f}")

    # Display schedule table
    st.write("### Repayment Schedule")
    st.dataframe(schedule.style.format("{:,.2f}"))

    # Disclaimer
    st.write("---")
    st.caption(
        "Disclaimer: This tool is for simulation purposes only and should not be considered financial advice. "
        "Please consult with a financial advisor or loan officer for accurate loan calculations."
    )
