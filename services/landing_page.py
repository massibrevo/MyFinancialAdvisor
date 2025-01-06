import streamlit as st

def show_landing_page():
    # Header Section
    st.title("🌟 FinancePro Planner 🌟")
    st.image(
        "financewebapp/images/finance.jpg",
        use_container_width=True,
        caption="FinancePro Planner"
    )
    st.write("### Welcome to FinancePro Planner. Optimize your financial future!")

    # Divider
    st.divider()

    # Key Features Section
    st.write("## 🚀 Key Features")
    st.markdown("""
    - **Smart Financial Planning:** Optimize your investments and achieve your financial goals effortlessly.
    - **Interactive Simulations:** Visualize different scenarios and make data-driven decisions.
    - **Beautiful Visualizations:** Track your growth with elegant and insightful charts.
    - **User-Friendly Chatbot:** Ask financial questions and get instant advice.
    """)

    # Divider
    st.divider()

    # Call-to-Action Section
    st.write("## 🏆 Why Choose FinancePro Planner?")
    st.markdown("""
    - Achieve financial freedom with tailored planning.
    - Harness the power of data to grow your wealth.
    - Plan your future with confidence and clarity.
    """)
    st.button("Get Started Now!", type="primary")

    # Testimonials Section
    st.write("## 🌟 Testimonials")
    col1, col2 = st.columns(2)
    with col1:
        st.image("https://via.placeholder.com/150", caption="Maria, Business Owner")
        st.write("*'FinancePro Planner transformed my financial strategy. Highly recommend!'*")
    with col2:
        st.image("https://via.placeholder.com/150", caption="John, Data Scientist")
        st.write("*'The best tool for interactive simulations. Brilliant charts and UX!'*")

    # Footer Section
    st.divider()
    st.write("💼 Brought to you by **Codicecaffe' Inc.** | Empowering financial growth one plan at a time.")
    st.caption(
        "Disclaimer: This app is for simulation purposes only and should not be considered financial advice. "
        "Always consult a certified financial advisor before making investment decisions."
    )
