DROP VIEW IF EXISTS dashboard_exercise_progress;

CREATE VIEW dashboard_exercise_progress AS
SELECT
    ep.exercise_name,
    ep.total_training_days,
    ep.recent_training_days,
    ep.recent_best,
    ep.all_time_best,
    ep.pct_of_best,

    ml.model_n_weeks,
    ml.current_weekly_best_1rm,
    ml.trend_slope,
    ml.predicted_next_1rm,
    ml.training_r2,
    ml.model_name

FROM exercise_progress ep
LEFT JOIN ML_progress_scores ml
    ON ep.exercise_name = ml.exercise_name;