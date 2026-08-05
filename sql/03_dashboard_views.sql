DROP VIEW IF EXISTS workout_summary;
DROP VIEW IF EXISTS exercise_progress;


CREATE VIEW workout_summary AS
SELECT
    Date,

    COUNT(*) AS n_sets,

    SUM(
        CASE
            WHEN Weight IS NOT NULL
             AND Reps IS NOT NULL
            THEN Weight * Reps
            ELSE 0
        END
    ) AS total_volume,

    

    COUNT(
        DISTINCT "Exercise Name"
    ) AS number_of_exercises

FROM cleaned_workouts

GROUP BY Date;


CREATE VIEW exercise_progress AS
WITH dataset_dates AS (
    SELECT
        MAX(Date) AS latest_date
    FROM set_metrics
),

historical_performance AS (
    SELECT
        exercise_name,
        MAX(est_1RM) AS all_time_best,
        COUNT(
            DISTINCT Date
        ) AS total_training_days

    FROM set_metrics

    GROUP BY exercise_name
),

recent_performance AS (
    SELECT
        exercise_name,
        MAX(est_1RM) AS recent_best,
        COUNT(
            DISTINCT Date
        ) AS recent_training_days

    FROM set_metrics
    CROSS JOIN dataset_dates

    WHERE Date >= date(
        latest_date,
        '-56 days'
    )

    GROUP BY exercise_name
)

SELECT
    h.exercise_name,
    h.total_training_days,
    r.recent_training_days,
    r.recent_best,
    h.all_time_best,

    ROUND(
        100.0 * r.recent_best
        / NULLIF(h.all_time_best, 0),
        1
    ) AS pct_of_best

FROM historical_performance AS h

JOIN recent_performance AS r
    ON h.exercise_name = r.exercise_name

WHERE h.total_training_days >= 5
  AND r.recent_training_days >= 2;