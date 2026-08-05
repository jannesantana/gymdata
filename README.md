# Gymdata

This is a data-analysis pipeline that generates valuable insights about the progress evolution of strength training exercises using SQL, Machine Learning and visualisation tools. 
The user provides a .csv file containing chronological logs of workout sessions and the application performs an SQL + Machine Learning analysis pipeline, displaying trends about personal gym data. 

This is an active personal learning project, inspired by a passion for Data Science and curiosity about how to implement its tools to improve my gym habits. Current model outputs should be interpreted as exploratory analytics rather than training, medical, or injury-prevention advice.

# Project status
Current release: v0.1 — preliminary portfolio version
The current version implements an end-to-end analytics pipeline for personal gym data:

* CSV ingestion into SQLite
* SQL-based cleaning and feature engineering
* weekly exercise and training-volume analysis
* recent-versus-historical progression metrics
* an interactive Streamlit dashboard
* per-exercise linear trend models
* walk-forward forecast validation
* comparison against a no-change baseline

The forecasting component predicts the next recorded weekly estimated 1RM, rather than performance in the next calendar week. Results are evaluated using mean absolute error and compared with a persistence baseline that assumes the next performance value will equal the current value.

