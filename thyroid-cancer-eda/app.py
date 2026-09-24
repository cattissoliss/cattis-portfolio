from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_PATH = Path(__file__).parent / "data" / "Thyroid_Diff.csv"
VARIABLES = ["Risk", "Gender", "Stage", "Pathology"]
RECURRENCE_ORDER = ["No", "Yes"]
RECURRENCE_COLORS = {"No": "#2563EB", "Yes": "#F59E0B"}


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and lightly validate the local copy of the UCI dataset."""
    data = pd.read_csv(DATA_PATH)
    required_columns = {*VARIABLES, "Recurred"}
    missing_columns = required_columns.difference(data.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"The dataset is missing required columns: {missing}")

    for column in required_columns:
        data[column] = data[column].astype(str).str.strip()

    return data


def overall_recurrence(data: pd.DataFrame) -> pd.DataFrame:
    counts = data["Recurred"].value_counts().reindex(RECURRENCE_ORDER, fill_value=0)
    return pd.DataFrame(
        {
            "Recurrence": counts.index,
            "Patients": counts.values,
            "Percentage": (counts.values / len(data) * 100).round(1),
        }
    )


def recurrence_crosstab(data: pd.DataFrame, variable: str) -> pd.DataFrame:
    category_order = data[variable].drop_duplicates()
    counts = pd.crosstab(data[variable], data["Recurred"]).reindex(
        index=category_order,
        columns=RECURRENCE_ORDER,
        fill_value=0,
    )

    summary = counts.rename(columns={"No": "No recurrence", "Yes": "Recurrence"})
    summary["Total"] = summary["No recurrence"] + summary["Recurrence"]
    summary["Recurrence (%)"] = (
        summary["Recurrence"].div(summary["Total"]).mul(100).round(1)
    )
    return summary.reset_index()


st.set_page_config(
    page_title="Thyroid Cancer Recurrence EDA",
    page_icon="📊",
    layout="wide",
)

st.title("Differentiated Thyroid Cancer Recurrence")
st.caption(
    "Descriptive analysis of 383 patients from the UCI Machine Learning Repository"
)

data = load_data()
overall = overall_recurrence(data)
no_row = overall.loc[overall["Recurrence"] == "No"].iloc[0]
yes_row = overall.loc[overall["Recurrence"] == "Yes"].iloc[0]

st.subheader("Overall recurrence")
metric_no, metric_yes, metric_total = st.columns(3)
metric_no.metric(
    "Without recurrence",
    f"{no_row['Patients']} patients",
)
metric_no.caption(f"{no_row['Percentage']:.1f}% of the sample")
metric_yes.metric(
    "With recurrence",
    f"{yes_row['Patients']} patients",
)
metric_yes.caption(f"{yes_row['Percentage']:.1f}% of the sample")
metric_total.metric("Total sample", f"{len(data)} patients")

with st.expander("View overall frequency table"):
    st.dataframe(
        overall.style.format({"Percentage": "{:.1f}%"}),
        hide_index=True,
        width="stretch",
    )

st.divider()
st.subheader("Recurrence by patient characteristic")
selected_variable = st.selectbox(
    "Choose a variable",
    VARIABLES,
    help="The table cross-tabulates recurrence within every category of the selected variable.",
)

summary = recurrence_crosstab(data, selected_variable)
chart_data = summary.melt(
    id_vars=[selected_variable, "Total", "Recurrence (%)"],
    value_vars=["No recurrence", "Recurrence"],
    var_name="Outcome",
    value_name="Patients",
)

figure = px.bar(
    chart_data,
    x=selected_variable,
    y="Patients",
    color="Outcome",
    barmode="group",
    color_discrete_map={
        "No recurrence": RECURRENCE_COLORS["No"],
        "Recurrence": RECURRENCE_COLORS["Yes"],
    },
    custom_data=["Total", "Recurrence (%)"],
    labels={selected_variable: selected_variable, "Patients": "Number of patients"},
    title=f"Recurrence status by {selected_variable.lower()}",
)
figure.update_traces(
    hovertemplate=(
        f"{selected_variable}: %{{x}}<br>"
        "%{fullData.name}: %{y}<br>"
        "Category total: %{customdata[0]}<br>"
        "Recurrence rate: %{customdata[1]:.1f}%<extra></extra>"
    )
)
figure.update_layout(
    legend_title_text="Recurrence status",
    hovermode="x unified",
    margin=dict(l=20, r=20, t=60, b=20),
)
figure.update_xaxes(type="category")
st.plotly_chart(figure, width="stretch")

st.markdown(f"**Cross-tabulation: recurrence by {selected_variable.lower()}**")
st.dataframe(
    summary.style.format({"Recurrence (%)": "{:.1f}%"}),
    hide_index=True,
    width="stretch",
)

st.caption(
    "Recurrence (%) is calculated within each category: recurrence count ÷ category total × 100."
)
st.markdown(
    "Source: [UCI Differentiated Thyroid Cancer Recurrence dataset]"
    "(https://archive.ics.uci.edu/dataset/915/differentiated+thyroid+cancer+recurrence) "
    "(CC BY 4.0)."
)
