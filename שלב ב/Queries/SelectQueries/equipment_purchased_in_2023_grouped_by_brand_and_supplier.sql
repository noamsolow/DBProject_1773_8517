-- Query to find equipment purchased in 2023 and grouped by brand and supplier
SELECT 
    e.name AS equipment_name,  -- Equipment name
    e.brand,                   -- Equipment brand
    COUNT(e.equipment_id) AS total_equipment  -- Total count of equipment purchased in 2023
FROM 
    Equipment e
JOIN 
    Equipment_Supplier es ON e.equipment_id = es.equipment_id
JOIN 
    Supplier s ON es.supplier_id = s.supplier_id
WHERE 
    EXTRACT(YEAR FROM e.purchase_date) = 2023  -- Filter for equipment purchased in 2023
GROUP BY 
    e.brand, e.name;  -- Group by brand and equipment name
