SELECT * 
FROM workouts
LIMIT 10;

SELECT DISTINCT "Set Order"
FROM workouts
ORDER BY "Set Order";
	

-- what exercises do I have?
SELECT DISTINCT "Exercise Name"
FROM workouts
ORDER BY "Exercise Name";

-- how *many* unique exercises do I have?
SELECT COUNT(DISTINCT "Exercise Name")
FROM workouts
ORDER BY "Exercise Name";

-- what do I train less?

SELECT "Exercise Name", COUNT(*) AS n_sets
FROM workouts
GROUP BY "Exercise Name"
ORDER BY n_sets DESC;

-- when did I start training? 

SELECT MIN(Date) AS first_workout, MAX(Date) AS last_workout
FROM workouts;

-- how many workout days?

SELECT COUNT(DISTINCT "Date") AS total_workouts
FROM workouts;

-- how much volume per set?

SELECT Date, "Exercise Name", Weight, Reps, Weight * Reps AS volume
FROM workouts
WHERE Weight IS NOT NULL
AND Reps IS NOT NULL
LIMIT 30;

-- what exercises have highest total volume?

SELECT "Exercise Name", SUM(Weight * Reps) AS total_volume
FROM cleaned_workouts
WHERE Weight IS NOT NULL
AND REPS IS NOT NULL
GROUP BY "Exercise Name"
ORDER BY total_volume DESC;


-- which exercises might be stagnating?

SELECT "Exercise Name", Date, SUM(Weight * Reps) AS total_volume
FROM cleaned_workouts
WHERE "Exercise Name" IS NOT "Running (Treadmill)"
AND Weight IS NOT NULL
AND REPS IS NOT NULL 
GROUP BY DATE
ORDER BY DATE DESC;

-- total volume per time and last PR?

SELECT Date, SUM(Weight * Reps) AS total_volume
FROM cleaned_workouts
WHERE "Exercise Name" != "Running (Treadmill)"
AND Weight IS NOT NULL
AND REPS IS NOT NULL
GROUP BY Date -- already produces one row per date
ORDER BY total_volume DESC
LIMIT 1;