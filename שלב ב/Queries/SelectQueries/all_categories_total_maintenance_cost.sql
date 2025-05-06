-- Query to show total maintenance cost for all categories (Cardio, Strength, Flexibility)
SELECT 
    'Cardio' AS category_name,  -- Hardcoded 'Cardio' category
    SUM(m.cost) AS total_maintenance_cost,  -- Total maintenance cost for Cardio
    AVG(m.cost) AS avg_maintenance_cost  -- Average maintenance cost for Cardio
FROM 
    Equipment e
JOIN 
    Maintenance m ON e.equipment_id = m.equipment_id
JOIN 
    CardioEquipment ce ON e.equipment_id = ce.equipment_id
UNION ALL
SELECT 
    'Strength' AS category_name,  -- Hardcoded 'Strength' category
    SUM(m.cost) AS total_maintenance_cost,  -- Total maintenance cost for Strength
    AVG(m.cost) AS avg_maintenance_cost  -- Average maintenance cost for Strength
FROM 
    Equipment e
JOIN 
    Maintenance m ON e.equipment_id = m.equipment_id
JOIN 
    StrengthEquipment se ON e.equipment_id = se.equipment_id
UNION ALL
SELECT 
    'Flexibility' AS category_name,  -- Hardcoded 'Flexibility' category
    SUM(m.cost) AS total_maintenance_cost,  -- Total maintenance cost for Flexibility
    AVG(m.cost) AS avg_maintenance_cost  -- Average maintenance cost for Flexibility
FROM 
    Equipment e
JOIN 
    Maintenance m ON e.equipment_id = m.equipment_id
JOIN 
    FlexibilityEquipment fe ON e.equipment_id = fe.equipment_id
ORDER BY 
    total_maintenance_cost DESC;  -- Sort by total maintenance cost
