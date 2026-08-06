from __future__ import annotations
import argparse

import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


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

exercise_data = weekly[weekly["exercise_name"]== selected_exercises].copy()

figure = px.line(exercise_data,x = "training_week",y = "weekly_best_1rm",markers=True,title=f"{selected_exercises}: weekly estimated 1RM",)

st.plotly_chart(figure,width='stretch')

st.subheader("Exercises furthest below historical best")

st.dataframe(progress.sort_values("pct_of_best"),width='content',)

st.subheader("Recent exercise trends")

trend_table = progress[["exercise_name", "pct_of_best", "recent_training_days", "trend_slope", "predicted_next_1rm","training_r2"]].sort_values("trend_slope")

st.dataframe(trend_table,width='stretch')

figure = px.scatter(progress,x="pct_of_best",y="trend_slope", size="recent_training_days",hover_name="exercise_name",title="Recent performance level versus trend",)

st.plotly_chart(figure,width='stretch',)

st.subheader("Forecast validation")

st.dataframe(validation.sort_values("mae_improvement_pct",ascending=False),width='stretch')

figure = px.scatter(
    validation,
    x="baseline_mae",
    y="model_mae",
    hover_name="exercise_name",
    size="test_predictions",
    title="Trend model versus naïve baseline",
)

st.plotly_chart(
    figure,width='stretch',
)


# model_mae < baseline_mae → model beats baseline
# model_mae > baseline_mae → baseline is better