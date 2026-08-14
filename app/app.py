from __future__ import annotations
import argparse

import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE = PROJECT_ROOT / "data" / "sample_gym.db"


def parse_arguments() -> argparse.Namespace: 
    parser = argparse.ArgumentParser(description=("Streamlit dashboard view."))
    
    
    parser.add_argument("--database", type=Path,default=DEFAULT_DATABASE,help="Path to the SQLite database.")
    arguments, _ = parser.parse_known_args()
    
    return arguments

arguments = parse_arguments()
DATABASE_PATH = (arguments.database.expanduser().resolve()) 

if not DATABASE_PATH.exists():
    st.error(
        f"Database not found: {DATABASE_PATH}\n\n"
        "Run the pipeline first or provide the correct "
        "--database argument.")
    st.stop()


@st.cache_data
def load_table(table_name: str, database_path: str) -> pd.DataFrame:
    
    
    allowed_tables = {"workout_summary","exercise_weekly","exercise_progress","ml_progress_scores","dashboard_exercise_progress", "ML_forecast_modeling", "ML_forecast_summary"}
   
    if table_name not in allowed_tables:
        raise ValueError(f'Unsupported table name : "{table_name}"') 
    
    with sqlite3.connect(database_path) as connection:
        return pd.read_sql_query(f'SELECT * FROM "{table_name}"',connection,)


DATABASE_PATH_STRING = str(DATABASE_PATH)

    
# building the actual streamlit web app dashboard

st.set_page_config(page_title = "Gym Analytics",layout="wide")
st.title("Gym Analytics")

weekly = load_table("exercise_weekly",DATABASE_PATH_STRING)
progress = load_table("dashboard_exercise_progress",DATABASE_PATH_STRING)
workouts = load_table("workout_summary",DATABASE_PATH_STRING)
validation = load_table("ML_forecast_summary",DATABASE_PATH_STRING)

selected_exercises = st.selectbox("Exercise",sorted(weekly["exercise_name"].dropna().unique()),)

# weekly exercise plot

exercise_data = weekly[weekly["exercise_name"]== selected_exercises].copy()

figure = px.line(exercise_data,x = "training_week",y = "weekly_best_1rm",markers=True,title=f"{selected_exercises}: weekly estimated 1RM",)
figure.update_xaxes(type = "category", title_text = "Year-Week")
figure.update_yaxes(title_text = "Weekly best 1 Rep Max")


figure.update_traces(hovertemplate= "Year-Week: %{x}<br>"
        "1RM: %{y:.2f}""<extra></extra>")

st.plotly_chart(figure,width='stretch')


# exercises very below historical best


st.subheader("Progress and model results")

st.dataframe(progress.sort_values("pct_of_best"),width='content',column_config={
        "exercise_name": "Exercise",
        "total_training_days": "Total Training Days",
        "recent_training_days": "Recent Training Days",
        "recent_best": "Recent Best (kg)",
        "all_time_best": "All Time Best (kg)",
        "pct_of_best": " % from best",
        "model_n_weeks": "Weeks window size"+"\n" +"for model",
        "current_weekly_best_1rm": "Current 1RM",
        "trend_slope": "Model Trend Slope",
        "predicted_next_1rm": "Projected next 1RM",
        "training_r2": "Training R²",
        "model_name": "Model Name"
    })


# slope trend from model lift vs % from best lift 

figure = px.scatter(
    progress,
    x="pct_of_best",
    y="trend_slope",
    size="recent_training_days",
    hover_name="exercise_name",
    hover_data=["recent_training_days"],
    labels={
        "pct_of_best": " % from best",
        "trend_slope": " Trend Slope",
        "recent_training_days": " Recent Training Days",
        "exercise_name": "Exercise Name",
    },
    title="Recent performance level vs trend",
)

figure.update_layout(
    xaxis_title="% of best lift",
    yaxis_title="Linear Trend Slope"
)

st.plotly_chart(figure,width='stretch',)

st.subheader("Forecast validation")

st.dataframe(validation.sort_values("mae_improvement_pct",ascending=False),width='stretch',column_config={
    "exercise_name": "Exercise",
    "test_predictions": "Test Predictions",
    "model_mae": "Model MAE",
    "baseline_mae": "Baseline MAE",
    "mae_improvement": "MAE Improvement",
    "mae_improvement_pct": "MAE Improvement (%)",
    "model_beats_baseline": "Model Beats Baseline",
})

figure = px.scatter(
    validation,
    x="baseline_mae",
    y="model_mae",
    hover_name="exercise_name",
    hover_data = ["test_predictions"],
    labels={"baseline_mae": " Baseline MAE",
            "model_mae": " Model MAE",
            "test_predictions": " Test Predictions"},
    size="test_predictions",
    title="Trend model versus naïve baseline",
)

figure.add_trace(
    go.Scatter(
        x=[0, 15],
        y=[0, 15],
        mode="lines",
        line=go.scatter.Line(color="gray"),
        showlegend=True,
        name = "y = x")
)

figure.update_layout(
    xaxis_title="Baseline MAE",
    yaxis_title="Model MAE"
)

st.plotly_chart(
    figure,width='stretch',
)


# model_mae < baseline_mae → model beats baseline
# model_mae > baseline_mae → baseline is better