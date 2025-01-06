import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def create_line_chart(years, investment_value, property_value, benchmark=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years,
        y=investment_value,
        mode='lines+markers',
        name='Investment Value',
        line=dict(color='blue')
    ))
    fig.add_trace(go.Scatter(
        x=years,
        y=property_value,
        mode='lines+markers',
        name='Property Value',
        line=dict(color='green')
    ))

    if benchmark:
        fig.add_trace(go.Scatter(
            x=years,
            y=benchmark,
            mode='lines',
            name='Benchmark (Inflation)',
            line=dict(dash='dot', color='red')
        ))

    fig.add_trace(go.Scatter(
        x=[years[-1], years[-1]],
        y=[investment_value[-1], property_value[-1]],
        mode='markers+text',
        name='Final Values',
        text=[
            f"€{investment_value[-1]:,.2f}",
            f"€{property_value[-1]:,.2f}"
        ],
        textposition='top center',
        marker=dict(size=10, color='purple')
    ))

    fig.update_layout(
        title="Financial Growth Over Time",
        xaxis_title="Years",
        yaxis_title="Value (€)",
        template="plotly_white",
    )
    return fig


def show_finance_pro_planner():
    st.title("FinancePro Planner")
    st.write("Plan and visualize your financial growth with interactive tools and insights.")
    
    # **Formulas in LaTeX**
    st.subheader("Formulas Used")
    st.latex(r"Investment\ Value = Initial\ Capital \cdot (1 + Investment\ Rate)^{Years}")
    st.latex(r"Property\ Value = Property\ Price \cdot (1 + Property\ Growth\ Rate)^{Years}")
    st.latex(r"Inflation\ Adjusted\ Value = Initial\ Value \cdot (1 + Inflation\ Rate)^{Years}")
    
    # **User Inputs**
    initial_capital = st.number_input("Initial Capital (€)", min_value=0, value=200000)
    monthly_savings = st.number_input("Monthly Savings (€)", min_value=0, value=600)
    investment_rate = st.slider("Investment Rate (% per year)", min_value=0.0, max_value=10.0, value=4.0)
    property_price = st.number_input("Property Price (€)", min_value=0, value=350000)
    mortgage_rate = st.slider("Mortgage Rate (% per year)", min_value=0.0, max_value=10.0, value=2.5)
    years = st.slider("Years to Simulate", min_value=5, max_value=50, value=30)
    inflation_rate = st.slider("Inflation Rate (% per year)", min_value=0.0, max_value=5.0, value=2.0)

    years_range = list(range(1, years + 1))
    investment_value = [initial_capital * (1 + investment_rate / 100) ** year for year in years_range]
    property_value = [property_price * (1 + 2.0 / 100) ** year for year in years_range]
    benchmark = [initial_capital * (1 + inflation_rate / 100) ** year for year in years_range]

    # **Visualization**
    st.plotly_chart(create_line_chart(years_range, investment_value, property_value, benchmark))

    # **Summary Table**
    summary_data = {
        "Years": years_range,
        "Investment Value (€)": investment_value,
        "Property Value (€)": property_value,
        "Benchmark Value (€)": benchmark,
    }
    df = pd.DataFrame(summary_data)
    st.dataframe(df.style.format("{:,.2f}"))

    # **Download in Excel**
    buffer = pd.ExcelWriter("summary.xlsx", engine="xlsxwriter")
    df.to_excel(buffer, index=False, sheet_name="Summary")
    buffer.close()
    st.download_button(
        label=["download_excel"],
        data=open("summary.xlsx", "rb").read(),
        file_name="financial_summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # **Legal Disclaimer**
    st.write("---")
    st.caption(
        "Disclaimer: This app is for simulation purposes only and should not be considered financial advice. "
        "Always consult a certified financial advisor before making investment decisions."
    )
