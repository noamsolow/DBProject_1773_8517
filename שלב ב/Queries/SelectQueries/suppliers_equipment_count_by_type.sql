-- Query to list Suppliers with the number of equipment they supply, including sub-equipment types
SELECT 
    s.name AS supplier_name, 
    COUNT(es.equipment_id) AS total_equipment_count,
    COUNT(ce.equipment_id) AS cardio_count,
    COUNT(se.equipment_id) AS strength_count,
    COUNT(fe.equipment_id) AS flexibility_count
FROM 
    Supplier s
JOIN 
    Equipment_Supplier es ON s.supplier_id = es.supplier_id
LEFT JOIN 
    CardioEquipment ce ON es.equipment_id = ce.equipment_id
LEFT JOIN 
    StrengthEquipment se ON es.equipment_id = se.equipment_id
LEFT JOIN 
    FlexibilityEquipment fe ON es.equipment_id = fe.equipment_id
GROUP BY 
    s.supplier_id
ORDER BY 
    total_equipment_count DESC;
