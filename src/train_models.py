from __future__ import annotations
import argparse


import sqlite3
from pathlib import Path

import numpy as np 
import pandas as pd
from sklearn.linear_model import LinearRegression

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE = PROJECT_ROOT / "data" / "sample_gym.db"


MODEL_WINDOW = 4
MIN_WEEKS = 3

def parse_arguments() -> argparse.Namespace: 
    parser = argparse.ArgumentParser(description=("Train exercise progression models."))
    
    
    parser.add_argument("--database", type=Path,default=DEFAULT_DATABASE,help="Path to the SQLite database.")
    
    return parser.parse_args()

def load_weekly_data(connection: sqlite3.Connection,) -> pd.DataFrame:
    """Load exercise-level weekly performance data"""
    
    query = """
        SELECT
            exercise_name,
            training_week,
            weekly_best_1rm,
            weekly_volume,
            n_sets
        FROM exercise_weekly
        WHERE weekly_best_1rm IS NOT NULL
        ORDER BY exercise_name, training_week
    """
    
    # this is necessary to avoid training the ML model on missing values
    # sorting in chronological order
    
    return pd.read_sql_query(query,connection)


def calculate_trend_scores(weekly_data: pd.DataFrame,) -> pd.DataFrame:
    """fit one recent linear trend model per exercise"""
    
    results: list[dict[str,object]] = []
    
    grouped_exercises = weekly_data.groupby("exercise_name")
    
    for exercise_name, exercise_data in grouped_exercises:
        recent = (exercise_data.sort_values("training_week").tail(MODEL_WINDOW)).copy() # uses at most MODEL_WINDOW recorded weeks for each exercise
        #sort values by training week -> selects the last MODEL_WINDOW rows and copies the dataframe for this exercise
        
        if len(recent) < MIN_WEEKS: # skeep exercises w/ very little data
            continue 
        
        x = np.arange(len(recent),dtype = float,).reshape(-1,1)
        y = recent["weekly_best_1rm"].to_numpy(dtype=float,)
        
        model = LinearRegression()
        model.fit(x,y)
        
        next_week_index = np.array([[len(recent)]],dtype=float) # creates the next value
        predicted_next_1rm = float(model.predict(next_week_index)[0]) # predicts/extrapolates it, assuming the recent linear trend continues
        
        results.append( {"exercise_name": exercise_name, "model_n_weeks": len(recent), "first_model_week": recent["training_week"].iloc[0],
                "last_model_week": recent["training_week"].iloc[-1],"current_weekly_best_1rm": float(y[-1]),"trend_slope": float(model.coef_[0]),
                "trend_intercept": float(model.intercept_),
                "predicted_next_1rm": predicted_next_1rm,
                "training_r2": float(model.score(x, y)), # how good the fit is
                "model_name": "linear_trend_v1",
            }
        )
        
    return pd.DataFrame(results)

def main() -> None:
    arguments = parse_arguments()
    DATABASE_PATH = (arguments.database.expanduser().resolve())
    
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DATABASE_PATH}")
    
    with sqlite3.connect(DATABASE_PATH) as connection:
        weekly_data = load_weekly_data(connection)
        
        if weekly_data.empty:
            raise ValueError("exercise_weekly contains no usable data")
        
        scores = calculate_trend_scores(weekly_data)
        
        if scores.empty:
            raise ValueError("no exercise had enough weeks to fit a model w/ desired window")
        
        scores.to_sql(name = "ML_progress_scores", con=connection,if_exists="replace",index=False)
        
    print(f"Created ML scores for {len(scores)} exercises")


if __name__ == "__main__":
    main()    

    
    
        
        
        
        
    
    
    
    