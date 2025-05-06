-- Query to calculate the average quantity of flexibility equipment bought together
SELECT 
    fe.material,                         -- Material of the flexibility equipment
    AVG(es.quantity) AS average_quantity_bought -- Average quantity bought for each flexibility equipment type
FROM 
    FlexibilityEquipment fe
JOIN 
    Equipment_Supplier es ON fe.equipment_id = es.equipment_id  -- Join with equipment supplier to get quantity
JOIN 
    Equipment e ON fe.equipment_id = e.equipment_id
GROUP BY 
    fe.material                            -- Grouping by the material type of the flexibility equipment
ORDER BY 
    average_quantity_bought DESC;          -- Ordering by the average quantity bought in descending order
