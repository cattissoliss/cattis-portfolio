from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_PATH = Path(__file__).parent / "data" / "Thyroid_Diff.csv"
VARIABLES = {
    "Risk": "risk",
    "Gender": "gender",
    "Stage": "stage",
    "Pathology": "pathology",
    "Age group": "age_group",
    "Smoking": "smoking",
    "History of smoking": "hx_smoking",
    "History of radiotherapy": "hx_radiotherapy",
    "Thyroid function": "thyroid_function",
    "Physical examination": "physical_examination",
    "Adenopathy": "adenopathy",
    "Response": "response",
    "Focality": "focality",
    "T classification": "t",
    "N classification": "n",
    "M classification": "m",
}
CATEGORY_ORDERS = {
    "risk": ["Low", "Intermediate", "High"],
    "gender": ["F", "M"],
    "stage": ["I", "II", "III", "IVA", "IVB"],
    "pathology": ["Micropapillary", "Papillary", "Follicular", "Hurthel cell"],
    "age_group": ["<30", "30–44", "45–59", "60+"],
    "smoking": ["No", "Yes"],
    "hx_smoking": ["No", "Yes"],
    "hx_radiotherapy": ["No", "Yes"],
    "thyroid_function": [
        "Euthyroid",
        "Clinical Hyperthyroidism",
        "Subclinical Hypothyroidism",
        "Clinical Hypothyroidism",
        "Subclinical Hyperthyroidism",
    ],
    "physical_examination": [
        "Multinodular goiter",
        "Single nodular goiter-right",
        "Single nodular goiter-left",
        "Diffuse goiter",
        "Normal",
    ],
    "adenopathy": ["No", "Right", "Bilateral", "Left", "Extensive", "Posterior"],
    "response": [
        "Excellent",
        "Indeterminate",
        "Biochemical Incomplete",
        "Structural Incomplete",
    ],
    "focality": ["Uni-Focal", "Multi-Focal"],
    "t": ["T1a", "T1b", "T2", "T3a", "T3b", "T4a", "T4b"],
    "n": ["N0", "N1a", "N1b"],
    "m": ["M0", "M1"],
}
RECURRENCE_ORDER = ["No", "Yes"]
RECURRENCE_COLORS = {"No": "#2563EB", "Yes": "#F59E0B"}


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load, clean, and validate the local copy of the UCI dataset."""
    data = pd.read_csv(DATA_PATH)
    data.columns = [
        column.strip().lower().replace(" ", "_") for column in data.columns
    ]
    data = data.rename(columns={"hx_radiothreapy": "hx_radiotherapy"})

    required_columns = {*VARIABLES.values(), "age", "recurred"} - {"age_group"}
    missing_columns = required_columns.difference(data.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"The dataset is missing required columns: {missing}")

    for column in data.select_dtypes(include="object").columns:
        data[column] = data[column].astype(str).str.strip()

    data["age"] = pd.to_numeric(data["age"], errors="raise").astype(int)
    data["age_group"] = pd.cut(
        data["age"],
        bins=[0, 29, 44, 59, float("inf")],
        labels=CATEGORY_ORDERS["age_group"],
    )

    return data


def overall_recurrence(data: pd.DataFrame) -> pd.DataFrame:
    counts = data["recurred"].value_counts().reindex(RECURRENCE_ORDER, fill_value=0)
    return pd.DataFrame(
        {
            "Recurrence": counts.index,
            "Patients": counts.values,
            "Percentage": (counts.values / len(data) * 100).round(1),
        }
    )


def recurrence_crosstab(
    data: pd.DataFrame, variable: str, display_name: str
) -> pd.DataFrame:
    counts = pd.crosstab(data[variable], data["recurred"]).reindex(
        index=CATEGORY_ORDERS[variable],
        columns=RECURRENCE_ORDER,
        fill_value=0,
    )

    summary = counts.rename(columns={"No": "No recurrence", "Yes": "Recurrence"})
    summary["Total"] = summary["No recurrence"] + summary["Recurrence"]
    summary["Recurrence (%)"] = (
        summary["Recurrence"].div(summary["Total"]).mul(100).round(1)
    )
    return summary.reset_index().rename(columns={variable: display_name})


def age_by_recurrence(data: pd.DataFrame) -> pd.DataFrame:
    summary = (
        data.groupby("recurred", sort=False, observed=True)["age"]
        .agg(["count", "mean", "median", "min", "max"])
        .round(1)
        .reset_index()
    )
    return summary.rename(
        columns={
            "recurred": "Recurrence status",
            "count": "Patients",
            "mean": "Mean age",
            "median": "Median age",
            "min": "Minimum age",
            "max": "Maximum age",
        }
    )


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

with st.expander("Data preparation and quality checks"):
    st.markdown(
        f"""
- **Rows retained:** {len(data)}
- **Original variables:** {len(data.columns) - 1}
- **Missing cells:** {int(data.isna().sum().sum())}
- **Exact duplicate rows retained:** {int(data.duplicated().sum())}

Values were trimmed, column names were standardized, the radiotherapy header was
corrected, and age was converted to an integer. Exact duplicate rows were retained
because the dataset has no patient identifier.
"""
    )

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
        overall,
        column_config={
            "Percentage": st.column_config.NumberColumn(format="%.1f%%")
        },
        hide_index=True,
        width="stretch",
    )

with st.expander("Explore age summary"):
    age_mean, age_median, age_range = st.columns(3)
    age_mean.metric("Mean age", f"{data['age'].mean():.1f} years")
    age_median.metric("Median age", f"{data['age'].median():.1f} years")
    age_range.metric("Age range", f"{data['age'].min()}–{data['age'].max()} years")

    st.markdown("**Age by recurrence status**")
    st.dataframe(
        age_by_recurrence(data),
        column_config={
            "Mean age": st.column_config.NumberColumn(format="%.1f"),
            "Median age": st.column_config.NumberColumn(format="%.1f"),
        },
        hide_index=True,
        width="stretch",
    )

st.divider()
st.subheader("Recurrence by patient characteristic")
selected_label = st.selectbox(
    "Choose a variable",
    list(VARIABLES),
    help="The table cross-tabulates recurrence within every category of the selected variable.",
)
selected_variable = VARIABLES[selected_label]

summary = recurrence_crosstab(data, selected_variable, selected_label)
chart_data = summary.melt(
    id_vars=[selected_label, "Total", "Recurrence (%)"],
    value_vars=["No recurrence", "Recurrence"],
    var_name="Outcome",
    value_name="Patients",
)

figure = px.bar(
    chart_data,
    x=selected_label,
    y="Patients",
    color="Outcome",
    barmode="group",
    color_discrete_map={
        "No recurrence": RECURRENCE_COLORS["No"],
        "Recurrence": RECURRENCE_COLORS["Yes"],
    },
    custom_data=["Total", "Recurrence (%)"],
    labels={selected_label: selected_label, "Patients": "Number of patients"},
    title=f"Recurrence status by {selected_label.lower()}",
)
figure.update_traces(
    hovertemplate=(
        f"{selected_label}: %{{x}}<br>"
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
figure.update_xaxes(
    type="category",
    tickangle=(
        -20
        if selected_label
        in {"Response", "Thyroid function", "Physical examination"}
        else 0
    ),
)
st.plotly_chart(figure, width="stretch")

st.markdown(f"**Cross-tabulation: recurrence by {selected_label.lower()}**")
st.dataframe(
    summary,
    column_config={
        "Recurrence (%)": st.column_config.NumberColumn(format="%.1f%%")
    },
    hide_index=True,
    width="stretch",
)

st.caption(
    "Recurrence (%) is calculated within each category: recurrence count ÷ category total × 100."
)
st.info(
    "This is descriptive analysis. Differences between groups do not establish "
    "causation, and percentages from very small categories should be interpreted cautiously."
)
st.markdown(
    "Source: [UCI Differentiated Thyroid Cancer Recurrence dataset]"
    "(https://archive.ics.uci.edu/dataset/915/differentiated+thyroid+cancer+recurrence) "
    "(CC BY 4.0)."
)
