from __future__ import annotations
import argparse

import sqlite3
from pathlib import Path

import numpy as np 
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# DATABASE_PATH = PROJECT_ROOT / "data" / "sample_gym.db"
DEFAULT_DATABASE = PROJECT_ROOT / "data" / "sample_gym.db"


MODEL_WINDOW = 8
MIN_TRAINING_OBSERVATIONS = 5

def parse_arguments() -> argparse.Namespace: 
    parser = argparse.ArgumentParser(description=("Validate exercise forecasting models"))
    
    
    parser.add_argument("--database", type=Path,default=DEFAULT_DATABASE,help="Path to the SQLite database.")
    
    return parser.parse_args()

def load_weekly_data(connection: sqlite3.Connection) -> pd.DataFrame:
    "Load chronological exercise-level performance data"
    
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
    
    data = pd.read_sql_query(query,connection)
    
    data["weekly_best_1rm"] = pd.to_numeric(data["weekly_best_1rm"],errors="coerce",)
    
    return data.dropna(subset=["weekly_best_1rm"]) # drop nan values for this specific column

def backtest_exercise(exercise_name: str,exercise_data: pd.DataFrame) -> pd.DataFrame:
    """Perform walk-forward validade for one exercise"""
    
    exercise_data = (exercise_data.sort_values("training_week").reset_index(drop=True)) # sort values chronologically and fix indexes
    
    predictions: list[dict[str,object]] = [] 
    
    # we pretend that some observations didn't happen, predict them and compare with the model prediction 
    
    for test_position in range(MIN_TRAINING_OBSERVATIONS, len(exercise_data)): 
        history = exercise_data.iloc[:test_position] # only observations before the test position
        
        training_data = history.tail(MODEL_WINDOW) # train only the most recent observations withing a window
        
        y_train = training_data["weekly_best_1rm"].to_numpy(dtype=float)
        x_train = np.arange(len(training_data),dtype=float).reshape(-1,1)
        
        model = LinearRegression()
        model.fit(x_train,y_train)
        
        x_next = np.array([[len(training_data)]],dtype=float)
        
        model_prediction = float( model.predict(x_next)[0] )
        
        actual_value = float( exercise_data["weekly_best_1rm"].iloc[test_position] )
        
        baseline_prediction = float(y_train[-1])
        
        training_week = str(exercise_data["training_week"].iloc[test_position])
        
        predictions.append({
                "exercise_name": exercise_name,
                "training_week": training_week,
                "training_observations": len(training_data),
                "actual_1rm": actual_value,
                "model_prediction": model_prediction,
                "baseline_prediction": baseline_prediction,
                "model_absolute_error": abs(
                    actual_value - model_prediction
                ),
                "baseline_absolute_error": abs(
                    actual_value - baseline_prediction
                ),
                "historical_trend_slope": float(
                    model.coef_[0]
                ),
            })
        
    return pd.DataFrame(predictions)
    
def run_backtest(weekly_data: pd.DataFrame) -> pd.DataFrame:
    """Backtest exercises with sufficient history"""
    
    results: list[pd.DataFrame] = []
    
    for exercise_name, exercise_data in weekly_data.groupby("exercise_name"):
        
        if len(exercise_data) <= MIN_TRAINING_OBSERVATIONS:
            continue
        
        exercise_results = backtest_exercise(exercise_name=str(exercise_name),exercise_data=exercise_data)
        
        if not exercise_results.empty:
            results.append(exercise_results)
            
    if not results:
        return pd.DataFrame() # empty data frame
    
    return pd.concat(results,ignore_index=True)

def summarize_backtest(predictions: pd.DataFrame) -> pd.DataFrame:
    
    summaries: list[dict[str, object]] = []
    
    for exercise_name, group in predictions.groupby("exercise_name"):
        
        # mae = mean absolute error 
        
        model_mae = mean_absolute_error(group["actual_1rm"],group["model_prediction"])

        baseline_mae = mean_absolute_error(group["actual_1rm"],group["baseline_prediction"])

        improvement = baseline_mae - model_mae

        if baseline_mae > 0:
            improvement_pct = (100.0 * improvement / baseline_mae)
        else:
            improvement_pct = np.nan
    
        summaries.append(
                {
                    "exercise_name": exercise_name,
                    "test_predictions": len(group),
                    "model_mae": float(model_mae),
                    "baseline_mae": float(baseline_mae),
                    "mae_improvement": float(improvement),
                    "mae_improvement_pct": float(
                        improvement_pct
                    ),
                    "model_beats_baseline": ( # true or false
                        model_mae < baseline_mae
                    ),
                }
            )

    return pd.DataFrame(summaries)


def main()->None:
    
    arguments = parse_arguments()
    
    DATABASE_PATH = (arguments.database.expanduser().resolve())
    
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DATABASE_PATH}")

    with sqlite3.connect(DATABASE_PATH) as connection:
        weekly_data = load_weekly_data(connection)
        
        predictions = run_backtest(weekly_data)
        
        if predictions.empty:
            raise ValueError("No exercises contained enough obs. for walk-forward validation")
        
        summaries = summarize_backtest(predictions)
        
        predictions.to_sql(name = "ML_forecast_modeling",con = connection, if_exists="replace", index = False)
        
        summaries.to_sql(name="ML_forecast_summary",con = connection,if_exists="replace",index= False)

    overall_model_mae = mean_absolute_error(predictions["actual_1rm"],predictions["model_prediction"])

    overall_baseline_mae = mean_absolute_error(predictions["actual_1rm"], predictions["baseline_prediction"])

    print(f"Historical predictions: {len(predictions)}")
    print(f"Model MAE:             {overall_model_mae:.2f}")
    print(f"Baseline MAE:          {overall_baseline_mae:.2f}")


if __name__ == "__main__":
    main()
        
        
        
        

        
        
        

        
        
        
        
        
        
        
        
        
        
    
    
    


    
