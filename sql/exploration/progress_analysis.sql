SELECT *
FROM exercise_weekly
ORDER BY exercise_name, training_week;


SELECT
    exercise_name,
    COUNT(*) AS weeks_trained,
    MIN(training_week) AS first_week,
    MAX(training_week) AS last_week
FROM exercise_weekly
GROUP BY exercise_name
ORDER BY weeks_trained DESC;

SELECT
    training_week,
    weekly_best_1rm,
    weekly_volume,
    n_sets
FROM exercise_weekly
WHERE exercise_name = 'Bench Press (Barbell)'
ORDER BY training_week;


-- compare each week with the previous week
-- lag allows us to retrieve value of column from prev ros in the result set without colapsing -> values for each row based on the partition 

SELECT
    exercise_name,
    training_week,
    weekly_best_1rm,

    LAG(weekly_best_1rm) OVER (
        PARTITION BY exercise_name
        ORDER BY training_week
    ) AS previous_week_best

FROM exercise_weekly
ORDER BY exercise_name, training_week;


-- computing weekly changes in percentages


WITH weekly_changes AS (
    SELECT
        exercise_name,
        training_week,
        weekly_best_1rm,

        LAG(weekly_best_1rm) OVER (
            PARTITION BY exercise_name
            ORDER BY training_week
        ) AS previous_week_best

    FROM exercise_weekly
)

SELECT
    exercise_name,
    training_week,
    weekly_best_1rm,
    previous_week_best,
    weekly_best_1rm - previous_week_best AS absolute_change, -- we saved the previous weekly best using lag 

    ROUND(
        100.0 * (weekly_best_1rm - previous_week_best)
        / NULLIF(previous_week_best, 0),
        1
    ) AS percentage_change

FROM weekly_changes
ORDER BY exercise_name, training_week;


-- using rolling averages to give a smoother trend


SELECT
    exercise_name,
    training_week,
    weekly_best_1rm,

    ROUND(
        AVG(weekly_best_1rm) OVER (
            PARTITION BY exercise_name 
            ORDER BY training_week
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW -- over 4 weeks
        ),
        1
    ) AS rolling_4_week_avg

FROM exercise_weekly
ORDER BY exercise_name, training_week;


-- inspecting for one exercise 

WITH rolling_performance AS (
    SELECT
        exercise_name,
        training_week,
        weekly_best_1rm,

        AVG(weekly_best_1rm) OVER (
            PARTITION BY exercise_name
            ORDER BY training_week
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ) AS rolling_4_week_avg

    FROM exercise_weekly
)

SELECT *
FROM rolling_performance
WHERE exercise_name = 'Bench Press (Barbell)'
ORDER BY training_week;


-- find all time best to every weekly row

SELECT
    exercise_name,
    training_week,
    weekly_best_1rm,

    MAX(weekly_best_1rm) OVER (
        PARTITION BY exercise_name
    ) AS all_time_best

FROM exercise_weekly
ORDER BY exercise_name, training_week;


-- retaining only weeks that matches all time best

WITH performance_with_best AS (
    SELECT
        exercise_name,
        training_week,
        weekly_best_1rm,

        MAX(weekly_best_1rm) OVER (
            PARTITION BY exercise_name
        ) AS all_time_best

    FROM exercise_weekly
)

SELECT
    exercise_name,
    training_week,
    weekly_best_1rm
FROM performance_with_best
WHERE weekly_best_1rm = all_time_best
ORDER BY exercise_name, training_week;

-- find the latest and colapse into 1 row per exercise 

WITH performance_with_best AS (
    SELECT
        exercise_name,
        training_week,
        weekly_best_1rm,

        MAX(weekly_best_1rm) OVER (
            PARTITION BY exercise_name
        ) AS all_time_best

    FROM exercise_weekly
),

pr_weeks AS (
    SELECT
        exercise_name,
        training_week,
        all_time_best
    FROM performance_with_best
    WHERE weekly_best_1rm = all_time_best -- selects the all time best from each exercise 
)

SELECT
    exercise_name,
    all_time_best,
    MAX(training_week) AS last_pr_week -- last week with a PR
FROM pr_weeks
GROUP BY exercise_name, all_time_best
ORDER BY last_pr_week;

-- comparing recent with history -> base the comparison with the most recent date in the database

-- for every exercise what is my recent best compared to my all-time best 

WITH dataset_dates AS (
    SELECT MAX(Date) AS latest_date
    FROM set_metrics
),

recent_performance AS (
    SELECT
        exercise_name,
        MAX(est_1rm) AS recent_best,
        COUNT(DISTINCT Date) AS recent_training_days
    FROM set_metrics
    CROSS JOIN dataset_dates
    WHERE Date >= date(latest_date, '-56 days')
    GROUP BY exercise_name
),

historical_performance AS (
    SELECT
        exercise_name,
        MAX(est_1rm) AS all_time_best
    FROM set_metrics
    GROUP BY exercise_name
)

SELECT
    h.exercise_name,
    r.recent_training_days,
    r.recent_best,
    h.all_time_best,

    ROUND(
        100.0 * r.recent_best
        / NULLIF(h.all_time_best, 0),
        1
    ) AS pct_of_best

FROM historical_performance h
LEFT JOIN recent_performance r
    ON h.exercise_name = r.exercise_name

ORDER BY pct_of_best;

-- filter insufficient data 

WITH dataset_dates AS (
    SELECT MAX(Date) AS latest_date
    FROM set_metrics
),

historical_performance AS (
    SELECT
        exercise_name,
        MAX(est_1rm) AS all_time_best,
        COUNT(DISTINCT Date) AS total_training_days
    FROM set_metrics
    GROUP BY exercise_name
),

recent_performance AS (
    SELECT
        exercise_name,
        MAX(est_1rm) AS recent_best,
        COUNT(DISTINCT Date) AS recent_training_days
    FROM set_metrics
    CROSS JOIN dataset_dates
    WHERE Date >= date(latest_date, '-56 days')
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

FROM historical_performance h
JOIN recent_performance r
    ON h.exercise_name = r.exercise_name

WHERE h.total_training_days >= 5
  AND r.recent_training_days >= 2

ORDER BY pct_of_best ASC;

