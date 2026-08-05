from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_DATABASE = PROJECT_ROOT / "data" / "sample_gym.db"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the complete gym analytics pipeline.")

    parser.add_argument("--input",type=Path,required=True,help="Path to the source gym CSV file.",)

    parser.add_argument("--database",type=Path,default=DEFAULT_DATABASE,help=("Path where the generated SQLite database will be saved. "f"Default: {DEFAULT_DATABASE}"))

    return parser.parse_args()


def run_script(relative_script_path: str,*arguments: str) -> None:
    script_path = PROJECT_ROOT / relative_script_path

    command = [sys.executable,str(script_path),*arguments]

    print(f"\nRunning: {' '.join(command)}")

    subprocess.run(command,cwd=PROJECT_ROOT,check=True)


def main() -> None:
    arguments = parse_arguments()

    input_path = arguments.input.expanduser().resolve()
    database_path = arguments.database.expanduser().resolve()

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input CSV not found: {input_path}")

    database_path.parent.mkdir(parents=True,exist_ok=True)

    run_script("src/build_database.py","--input",str(input_path),"--output",str(database_path),)

    run_script("src/train_models.py","--database",str(database_path),)

    run_script("src/validate_forecast.py","--database",str(database_path),)

    run_script("src/apply_post_ml_sql.py","--database",str(database_path),)

    print("\nPipeline completed successfully.")
    print(f"Database: {database_path}")


if __name__ == "__main__":
    main()
    
    
    