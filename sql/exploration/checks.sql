SELECT *
FROM ml_progress_scores
ORDER BY trend_slope;


SELECT exercise_name, model_n_weeks, current_weekly_best_1rm, trend_slope, predicted_next_1rm, training_r2
FROM ml_progress_scores
WHERE model_n_weeks >= 5
GROUP BY trend_slope;

SELECT *
FROM ml_progress_scores;

SELECT *
FROM dashboard_exercise_progress;

-- quering individual historical predictions 

SELECT exercise_name, training_week, actual_1rm, model_prediction,baseline_prediction,model_absolute_error,baseline_absolute_error
FROM ML_forecast_modeling
ORDER BY exercise_name, training_week;

SELECT *
FROM ml_forecast_summary
ORDER BY mae_improvement_pct DESC;

SELECT * 
FROM set_metrics 
WHERE exercise_name  = "Leg Press"
ORDER BY volume DESC

