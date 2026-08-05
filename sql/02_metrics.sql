DROP TABLE IF EXISTS exercise_weekly;
DROP TABLE IF EXISTS exercise_summary;
DROP TABLE IF EXISTS set_metrics;


CREATE TABLE set_metrics AS
SELECT
    Date,
    "Exercise Name" AS exercise_name,
    set_order_nbr,
    set_type,
    Weight,
    Reps,
    Weight * Reps AS volume,

    CASE
        WHEN Weight IS NOT NULL
         AND Reps IS NOT NULL
         AND Reps > 0
        THEN Weight * (1 + Reps / 30.0)
        ELSE NULL
    END AS est_1RM

FROM cleaned_workouts

WHERE Weight IS NOT NULL
  AND Reps IS NOT NULL
  AND "Exercise Name" != 'Running (Treadmill)';


CREATE TABLE exercise_summary AS
SELECT
    exercise_name,

    COUNT(*) AS n_sets,
    SUM(volume) AS total_volume,
    MAX(Weight) AS Best_weight,
    MAX(est_1RM) AS best_1RM,
    MIN(Date) AS first_seen,
    MAX(Date) AS last_seen

FROM set_metrics

GROUP BY exercise_name;


CREATE TABLE exercise_weekly AS
SELECT
    exercise_name,
    strftime('%Y-%W', Date) AS training_week,

    COUNT(*) AS n_sets,
    SUM(volume) AS weekly_volume,
    MAX(est_1RM) AS weekly_best_1rm

FROM set_metrics

GROUP BY
    exercise_name,
    training_week;