-- Main Program 2: Equipment and Maintenance System
DO $$
DECLARE
    equipment_cursor REFCURSOR;
    equipment_rec RECORD;
    supplier_id INTEGER := 1311; -- Using supplier from your sample data
    record_count INTEGER := 0;
BEGIN
    RAISE NOTICE '=== EQUIPMENT AND MAINTENANCE SYSTEM ===';
    RAISE NOTICE 'Date: %', CURRENT_DATE;
    RAISE NOTICE '==========================================';
    
    -- Call Function 2: Get equipment maintenance status
    RAISE NOTICE 'Step 1: Getting equipment maintenance status...';
    
    BEGIN
        equipment_cursor := get_equipment_maintenance_status();
        
        RAISE NOTICE 'EQUIPMENT MAINTENANCE REPORT:';
        RAISE NOTICE '%-6s %-20s %-12s %-15s %-8s', 
                     'ID', 'Name', 'Category', 'Warranty', 'Status';
        RAISE NOTICE '%', REPEAT('-', 70);
        
        LOOP
            FETCH equipment_cursor INTO equipment_rec;
            EXIT WHEN NOT FOUND;
            
            record_count := record_count + 1;
            RAISE NOTICE '%-6s %-20s %-12s %-15s %-8s',
                        equipment_rec.equipment_id,
                        LEFT(COALESCE(equipment_rec.name, 'N/A'), 20),
                        LEFT(COALESCE(equipment_rec.category, 'N/A'), 12),
                        COALESCE(equipment_rec.warranty_expiry::TEXT, 'N/A'),
                        equipment_rec.warranty_status;
                        
            -- Limit output to first 5 for readability
            IF record_count >= 5 THEN
                RAISE NOTICE '... (showing first 5 records)';
                EXIT;
            END IF;
        END LOOP;
        
        CLOSE equipment_cursor;
        RAISE NOTICE 'Total equipment records processed: %', record_count;
        
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Error getting equipment status: %', SQLERRM;
    END;
    
    RAISE NOTICE '';
    RAISE NOTICE 'Step 2: Processing equipment orders for supplier %...', supplier_id;
    
    -- Call Procedure 2: Process equipment orders
    BEGIN
        CALL process_equipment_orders(supplier_id, '2024-01-01');
        
        RAISE NOTICE 'Equipment order processing completed!';
        
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Error processing equipment orders: %', SQLERRM;
    END;
    
    RAISE NOTICE '';
    RAISE NOTICE '=== EQUIPMENT AND MAINTENANCE COMPLETED ===';
END;
$$;