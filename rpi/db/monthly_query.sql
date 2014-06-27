SELECT 
	diff.day, sum(diff.result) 
FROM 
(
	SELECT 
		date_trunc('day', antu.created_at + interval '6 hours') AS day, 
		antu.value - lag(antu.value, 1, CAST(0 AS real)) OVER (ORDER BY antu.id) AS result 
		FROM
		(
			SELECT * 
			FROM measurements
			WHERE sensor_id=2
		) antu
			
) diff
GROUP BY diff.day 
ORDER BY day;
