DROP TABLE IF EXISTS cleaned_workouts;

CREATE TABLE cleaned_workouts AS
SELECT
    *,

    CASE
        WHEN "Set Order" GLOB '[0-9]*'
        THEN CAST("Set Order" AS INTEGER)
        ELSE NULL
    END AS set_order_nbr,

    CASE
        WHEN "Set Order" GLOB '[A-Za-z]'
        THEN "Set Order"
        ELSE 'N'
    END AS set_type

FROM workouts;








