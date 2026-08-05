from __future__ import annotations
import sqlite3
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1] # root based on the location of database.py
DATABASE_PATH = PROJECT_ROOT / "data" / "sample_gym.db"

def read_query(query: str) -> pd.DataFrame: 
    # query should be a string containing SQL and the function retutnr a pandas dataframe
    
    """Run a SQL SELECT query and return the result as a DataFrame."""
    
    
    if not DATABASE_PATH.exists():
        raise FileNotFoundError (f"Database not found at {DATABASE_PATH}")
    
    database_uri = f"file:{DATABASE_PATH}?mode=ro"
    
    with sqlite3.connect(database_uri,uri=True) as connection: # creates the connections
        return pd.read_sql_query(query, connection) 
    # executes the query opening sqlite in read-only mode to avoid accidental rewrites
    
    

