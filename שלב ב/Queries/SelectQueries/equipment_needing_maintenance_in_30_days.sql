-- Query to find equipment that needs maintenance in the next 30 days
SELECT 
    e.equipment_id,              -- Equipment ID
    e.name AS equipment_name,    -- Equipment name
    m.service_date,              -- Service date for maintenance
    m.cost AS maintenance_cost   -- Maintenance cost
FROM 
    Equipment e
JOIN 
    Maintenance m ON e.equipment_id = m.equipment_id
WHERE 
    m.service_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'  -- Maintenance within the next 30 days
ORDER BY 
    m.service_date;  -- Order by service date
