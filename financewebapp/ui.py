"""Shared Streamlit components for the simulation pages."""

from io import BytesIO

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

COLORS = ("#4f46e5", "#078271", "#b45309")


def euro(amount: float) -> str:
    digits = f"{amount:,.0f}".replace(",", ".")
    return f"€ {digits}"


def page_heading(title: str, description: str) -> None:
    st.title(title)
    st.markdown(description)


def chart(frame: pd.DataFrame, x: str, series: tuple[str, ...], *, title: str) -> None:
    figure = go.Figure()
    for label, color in zip(series, COLORS, strict=False):
        figure.add_trace(go.Scatter(
            x=frame[x], y=frame[label], name=label, mode="lines",
            line={"color": color, "width": 3},
            hovertemplate="€ %{y:,.0f}<extra>%{fullData.name}</extra>",
        ))
    figure.update_layout(
        title={"text": title, "font": {"size": 17}},
        height=380, margin={"l": 14, "r": 20, "t": 56, "b": 24},
        hovermode="x unified", separators=",.",
        legend={"orientation": "h", "y": -0.25},
        xaxis={"title": x, "showgrid": False},
        yaxis={"tickprefix": "€ ", "separatethousands": True},
    )
    st.plotly_chart(
        figure, width="stretch", config={"displaylogo": False, "scrollZoom": False},
    )


def make_workbook(frame: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        frame.to_excel(writer, index=False, sheet_name="Simulazione")
        workbook = writer.book
        sheet = writer.sheets["Simulazione"]
        sheet.freeze_panes(1, 1)
        sheet.autofit()
        sheet.set_column(1, len(frame.columns) - 1, None, workbook.add_format({
            "num_format": '#,##0.00 "€"',
        }))
    return output.getvalue()


def results_table(frame: pd.DataFrame, name: str) -> None:
    st.dataframe(
        frame, hide_index=True, width="stretch",
        column_config={
            label: st.column_config.NumberColumn(format="€ %.2f")
            for label in frame.columns[1:]
        },
    )
    st.download_button(
        "Scarica Excel", data=make_workbook(frame), file_name=f"{name}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        icon=":material/download:", on_click="ignore",
    )


def save_summary(page: str, summary: str) -> None:
    st.session_state.setdefault("simulation_summaries", {})[page] = summary
