-- Query to find suppliers who provide cardio equipment with heart monitors, ordered by maintenance cost
SELECT 
    s.name AS supplier_name,        -- Supplier name
    s.contact_number AS supplier_phone, -- Supplier phone number
    s.email AS supplier_email,      -- Supplier email
    e.name AS equipment_name,       -- Equipment name
    SUM(m.cost) AS total_maintenance_cost  -- Total maintenance cost for each equipment
FROM 
    Supplier s
JOIN 
    Equipment_Supplier es ON s.supplier_id = es.supplier_id
JOIN 
    CardioEquipment ce ON es.equipment_id = ce.equipment_id
JOIN 
    Equipment e ON ce.equipment_id = e.equipment_id
JOIN 
    Maintenance m ON e.equipment_id = m.equipment_id
WHERE 
    ce.has_heart_rate_monitor = TRUE  -- Only Cardio equipment with heart monitors
GROUP BY 
    s.supplier_id, e.equipment_id
ORDER BY 
    total_maintenance_cost ASC;  -- Order by the total maintenance cost (ascending)
