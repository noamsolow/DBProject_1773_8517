-- Query to get the 50 dates with the most maintenance, ordered by maintenance cost and total cost for each date
SELECT 
    m.service_date,              -- Service date for maintenance
    COUNT(m.maintenance_id) AS total_maintenance_count,  -- Total count of maintenance events on this date
    SUM(m.cost) AS total_cost    -- Total cost for maintenance on this date
FROM 
    Maintenance m
GROUP BY 
    m.service_date
ORDER BY 
    total_cost DESC  -- Order by the total cost in descending order
LIMIT 50;  -- Limit to the top 50 dates with the most maintenance
