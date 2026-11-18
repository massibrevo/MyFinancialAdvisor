import streamlit as st


def show_landing_page(pages: list[tuple[object, str, str, str]]) -> None:
    st.html("""
        <section class="mfa-hero" aria-labelledby="mfa-home-title">
          <div class="mfa-brand">MyFinancialAdvisor</div>
          <h1 id="mfa-home-title">Dai un numero<br>alle tue scelte.</h1>
          <p>Confronta casa e affitto, simula un mutuo e misura
             quanto potrebbero valere i tuoi risparmi alla pensione.</p>
        </section>
    """)
    st.subheader("Simulatori", anchor=False)
    columns = st.columns(3, gap="medium")
    for column, (page, title, description, icon) in zip(columns, pages[:3], strict=True):
        with column, st.container(border=True):
            st.page_link(page, label=title, icon=icon)
            st.caption(description)

    with st.container(border=True):
        page, title, description, icon = pages[-1]
        st.page_link(page, label=title, icon=icon)
        st.caption(description)

    st.caption("Usa i risultati per confrontare le tue ipotesi. Le simulazioni hanno scopo informativo.")
