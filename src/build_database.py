from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "sample_gym.csv"
DEFAULT_DATABASE = PROJECT_ROOT / "data" / "sample_gym.db"
BUILD_SQL_DIRECTORY = PROJECT_ROOT / "sql" 

REQUIRED_COLUMNS = {"Date", "Exercise Name", "Set Order", "Weight", "Reps", "Duration (minutes)"}

def parse_arguments() -> argparse.Namespace: 
    parser = argparse.ArgumentParser(description=("Build the gym analytics SQLite database"))
    
    parser.add_argument("--input", type=Path, required=True,default=DEFAULT_INPUT, help="Input workout CSV")
    
    parser.add_argument("--output", type=Path,required=True,default=DEFAULT_DATABASE,help="Output SQLite database")
    
    return parser.parse_args()


def load_csv(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"Input CSV path not found: {csv_path}")
    
    data = pd.read_csv(csv_path)
    missing_columns = REQUIRED_COLUMNS - set(data.columns) 
    
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))

        raise ValueError(f"CSV is missing required columns: {missing}")
    
    parsed_dates = pd.to_datetime(data["Date"],errors="raise")

    data["Date"] = parsed_dates.dt.strftime("%Y-%m-%d")

    return data

    
def execute_sql_scripts(connection: sqlite3.Connection) -> None:
    scripts = sorted(BUILD_SQL_DIRECTORY.glob("*.sql")) # sort scripts by number to execute them in the proper order

    if not scripts:
        raise FileNotFoundError(f"No SQL scripts found in "f"{BUILD_SQL_DIRECTORY}")

    for script_path in scripts:
        print(f"Executing {script_path.name}")

        sql = script_path.read_text(encoding="utf-8")

        connection.executescript(sql)

def build_database(input_path: Path,output_path: Path) -> None:
    data = load_csv(input_path)

    output_path.parent.mkdir(parents=True,exist_ok=True)

    # Rebuilding from scratch prevents old tables or views
    # from remaining in the demonstration database.
    output_path.unlink(missing_ok=True) # ?

    with sqlite3.connect(output_path) as connection:
        data.to_sql(name="workouts",con=connection,if_exists="replace",index=False,)

        execute_sql_scripts(connection)

    print(f"Database created at: {output_path}")


def main() -> None:
    arguments = parse_arguments()

    build_database(input_path=arguments.input.expanduser().resolve(),output_path=arguments.output.expanduser().resolve())


if __name__ == "__main__":
    main()
