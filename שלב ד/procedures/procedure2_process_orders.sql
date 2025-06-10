-- Procedure 2: Process equipment orders (FIXED)
CREATE OR REPLACE PROCEDURE process_equipment_orders(
    IN p_supplier_id INTEGER,
    IN p_order_date DATE DEFAULT CURRENT_DATE
)
LANGUAGE plpgsql AS $$
DECLARE
    supplier_name TEXT;
    order_rec RECORD;
    total_cost NUMERIC := 0;
    order_count INTEGER := 0;
    
    -- Cursor for pending orders
    order_cursor CURSOR FOR
        SELECT es.equipment_id, es.quantity, es.supply_date, e.name, e.category
        FROM equipment_supplier es
        JOIN equipment e ON es.equipment_id = e.equipment_id
        WHERE es.pid = p_supplier_id 
        AND es.supply_date >= p_order_date
        ORDER BY es.supply_date;
BEGIN
    -- Get supplier name from person table
    SELECT firstname || ' ' || lastname INTO supplier_name
    FROM person 
    WHERE pid = p_supplier_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Supplier with ID % not found', p_supplier_id;
    END IF;
    
    RAISE NOTICE 'Processing equipment orders for supplier: % (ID: %)', 
                 supplier_name, p_supplier_id;
    RAISE NOTICE 'Orders from date: %', p_order_date;
    RAISE NOTICE '========================================';
    
    -- Process each order
    FOR order_rec IN order_cursor LOOP
        BEGIN
            DECLARE
                item_cost NUMERIC;
                base_price NUMERIC;
            BEGIN
                -- Calculate cost based on equipment category
                base_price := CASE 
                    WHEN order_rec.category = 'Strength' THEN 200.00
                    WHEN order_rec.category = 'Cardio' THEN 500.00
                    WHEN order_rec.category = 'Flexibility' THEN 50.00
                    ELSE 100.00
                END;
                
                item_cost := order_rec.quantity * base_price;
                total_cost := total_cost + item_cost;
                order_count := order_count + 1;
                
                RAISE NOTICE 'Order %: % units of % (ID: %)', 
                            order_count, 
                            order_rec.quantity, 
                            order_rec.name, 
                            order_rec.equipment_id;
                RAISE NOTICE '  Category: % | Unit Price: $% | Total: $%', 
                            order_rec.category, base_price, item_cost;
                RAISE NOTICE '  Supply Date: %', order_rec.supply_date;
                RAISE NOTICE '  --------------------------------';
            END;
            
        EXCEPTION
            WHEN OTHERS THEN
                RAISE NOTICE 'ERROR processing equipment ID %: %', order_rec.equipment_id, SQLERRM;
                CONTINUE;
        END;
    END LOOP;
    
    -- Final summary
    IF order_count = 0 THEN
        RAISE NOTICE 'No orders found for supplier % on or after %', p_supplier_id, p_order_date;
    ELSE
        RAISE NOTICE '========================================';
        RAISE NOTICE 'SUMMARY for %:', supplier_name;
        RAISE NOTICE 'Total Orders Processed: %', order_count;
        RAISE NOTICE 'Total Cost: $%', total_cost;
        RAISE NOTICE 'Average Order Value: $%', ROUND(total_cost / order_count, 2);
    END IF;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error processing equipment orders: %', SQLERRM;
END;
$$;