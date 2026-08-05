from __future__ import annotations
import argparse

import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE = PROJECT_ROOT / "data" / "sample_gym.db"

# DATABASE_PATH = PROJECT_ROOT / "data" / "sample_gym.db"
SQL_DIRECTORY = PROJECT_ROOT / "sql" / "post_ml"

def parse_arguments() -> argparse.Namespace: 
    parser = argparse.ArgumentParser(description=("Apply post-ML SQL views"))
    
    
    parser.add_argument("--database", type=Path,default=DEFAULT_DATABASE,help="Path to the SQLite database.")
    
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    
    DATABASE_PATH = (arguments.database.expanduser().resolve())
    
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DATABASE_PATH}")

    scripts = sorted(SQL_DIRECTORY.glob("*.sql"))

    with sqlite3.connect(DATABASE_PATH) as connection:
        for script_path in scripts:
            print(f"Executing {script_path.name}")

            connection.executescript(script_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()