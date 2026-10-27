SELECT * 
FROM IMAGES 
WHERE 		time_to_post >= '2026-10-26 00:00:00'
		and time_to_post <= '2026-10-27 00:00:00'
UNION
SELECT * 
FROM VIDEOS 
WHERE 		time_to_post >= '2026-10-26 00:00:00'
		and time_to_post <= '2026-10-27 00:00:00'
ORDER BY time_to_post ASC