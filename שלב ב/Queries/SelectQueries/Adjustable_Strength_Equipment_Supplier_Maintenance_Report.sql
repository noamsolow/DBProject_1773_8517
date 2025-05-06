
SELECT 
    s.name AS supplier_name,       -- Supplier name
    COUNT(m.maintenance_id) AS maintenance_count  -- Number of maintenance records for all equipment supplied by the supplier
FROM 
    Supplier s
JOIN 
    Equipment_Supplier es ON s.supplier_id = es.supplier_id
JOIN 
    StrengthEquipment se ON es.equipment_id = se.equipment_id
JOIN 
    Equipment e ON se.equipment_id = e.equipment_id
JOIN 
    Maintenance m ON e.equipment_id = m.equipment_id
WHERE 
    se.adjustable = TRUE                          -- Only adjustable equipment
    AND se.max_weight > 120                       -- Only strength equipment with a max weight capacity of over 120
GROUP BY 
    s.supplier_id                                -- Group by supplier only
ORDER BY 
    maintenance_count ASC;                       -- Order by the least amount of maintenance (ascending)
