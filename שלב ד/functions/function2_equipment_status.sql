-- Function 2: Get equipment maintenance status (SIMPLIFIED)
CREATE OR REPLACE FUNCTION get_equipment_maintenance_status()
RETURNS REFCURSOR AS $$
DECLARE
    equipment_cursor REFCURSOR := 'equipment_maintenance_cursor';
BEGIN
    OPEN equipment_cursor FOR
        SELECT 
            e.equipment_id,
            e.name,
            e.category,
            e.brand,
            e.purchase_date,
            e.warranty_expiry,
            CASE 
                WHEN e.warranty_expiry < CURRENT_DATE THEN 'EXPIRED'
                WHEN e.warranty_expiry < CURRENT_DATE + INTERVAL '30 days' THEN 'EXPIRING_SOON'
                ELSE 'VALID'
            END as warranty_status,
            COUNT(m.contract_id) as maintenance_count,
            MAX(cj.service_date) as last_maintenance_date,
            SUM(cj.cost) as total_maintenance_cost
        FROM equipment e
        LEFT JOIN maintenance m ON e.equipment_id = m.equipment_id
        LEFT JOIN contract_job cj ON m.contract_id = cj.contract_id
        GROUP BY e.equipment_id, e.name, e.category, e.brand, e.purchase_date, e.warranty_expiry
        ORDER BY e.equipment_id;
    
    RETURN equipment_cursor;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error creating equipment maintenance cursor: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;