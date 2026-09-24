# Thyroid Cancer Recurrence EDA

A small Streamlit dashboard for demonstrating frequency distributions and
cross-tabulation with the UCI Differentiated Thyroid Cancer Recurrence dataset.

## Run locally

From this directory:

    uv venv
    uv pip install -r requirements.txt
    uv run streamlit run app.py

The dashboard opens at http://localhost:8501.

## Analysis shown

- Overall recurrence counts and percentages
- Cross-tabulation of recurrence by Risk, Gender, Stage, Pathology, Age group,
  Smoking, Response, or Focality
- Within-category recurrence percentages
- Interactive grouped Plotly bar chart and its underlying summary table
- Data-cleaning checks and age summaries overall and by recurrence status

The included data/Thyroid_Diff.csv is the original file downloaded from the
[UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/915/differentiated+thyroid+cancer+recurrence).
The dataset is licensed under CC BY 4.0.
