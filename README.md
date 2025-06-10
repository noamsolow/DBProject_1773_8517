# דוח פרויקט - שלב ד

## תוכן עניינים

1. [סקירה כללית](#סקירה-כללית)
2. [פונקציות (Functions)](#פונקציות-functions)
3. [פרוצדורות (Procedures)](#פרוצדורות-procedures)
4. [טריגרים (Triggers)](#טריגרים-triggers)
5. [תוכניות ראשיות (Main Programs)](#תוכניות-ראשיות-main-programs)
6. [קבצים שהועלו לגיט](#קבצים-שהועלו-לגיט)

---

## סקירה כללית

שלב ד מתמקד בפיתוח תוכניות PL/pgSQL מתקדמות עבור מערכת ניהול המכון הספורטיבי. המערכת כוללת 8 רכיבי תוכנה עיקריים:

- **2 פונקציות** - עיבוד נתונים וחישובים מורכבים
- **2 פרוצדורות** - ביצוע פעולות עדכון ועיבוד עסקי
- **2 טריגרים** - אימות נתונים והגנה על שלמות המידע
- **2 תוכניות ראשיות** - אינטגרציה וביצוע הפונקציות והפרוצדורות

### תכונות PL/pgSQL שיושמו:
✅ **Cursors** - מחוונים מפורשים וחזרת Ref Cursor  
✅ **DML Operations** - פעולות INSERT, UPDATE עם אימות  
✅ **Conditionals** - הסתעפויות IF/ELSE מורכבות  
✅ **Loops** - לולאות FOR ועיבוד איטרטיבי  
✅ **Exception Handling** - טיפול שגיאות מקיף  
✅ **Records** - שימוש בטיפוסי RECORD למבני נתונים  

---

## פונקציות (Functions)

### פונקציה 1: `get_worker_shift_summary`

**תיאור מילולי:**
פונקציה המחשבת סיכום משמרות עבור עובד מסוים, כולל סה"כ שעות, שעות נוספות וחישוב שכר מוערך. הפונקציה משתמשת במחוון מפורש (explicit cursor) לעבור על כל המשמרות של העובד ומחשבת נתונים סטטיסטיים מתקדמים.

**קוד הפונקציה:**
```sql
CREATE OR REPLACE FUNCTION get_worker_shift_summary(worker_id INTEGER)
RETURNS TABLE(
    worker_name TEXT,
    total_shifts INTEGER,
    total_hours NUMERIC,
    overtime_hours NUMERIC,
    total_pay NUMERIC
) AS $$
DECLARE
    worker_full_name TEXT;
    worker_job TEXT;
    shift_rec RECORD;
    hourly_wage NUMERIC := 15.00;
    overtime_rate NUMERIC := 22.50;
    shift_cursor CURSOR FOR 
        SELECT date, clock_in, clock_out 
        FROM shift 
        WHERE pid = worker_id;
BEGIN
    -- Get worker information
    SELECT p.firstname || ' ' || p.lastname, w.job
    INTO worker_full_name, worker_job
    FROM person p
    JOIN worker w ON p.pid = w.pid
    WHERE p.pid = worker_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Worker with ID % not found', worker_id;
    END IF;
    
    -- Initialize counters
    total_shifts := 0;
    total_hours := 0;
    overtime_hours := 0;
    
    -- Open explicit cursor and process shifts
    OPEN shift_cursor;
    LOOP
        FETCH shift_cursor INTO shift_rec;
        EXIT WHEN NOT FOUND;
        
        DECLARE
            shift_hours NUMERIC;
        BEGIN
            shift_hours := EXTRACT(EPOCH FROM (shift_rec.clock_out - shift_rec.clock_in)) / 3600;
            
            total_shifts := total_shifts + 1;
            total_hours := total_hours + shift_hours;
            
            IF shift_hours > 8 THEN
                overtime_hours := overtime_hours + (shift_hours - 8);
            END IF;
        END;
    END LOOP;
    CLOSE shift_cursor;
    
    -- Calculate total pay
    total_pay := (total_hours - overtime_hours) * hourly_wage + 
                 overtime_hours * overtime_rate;
    
    worker_name := worker_full_name;
    RETURN NEXT;
    
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RAISE EXCEPTION 'No data found for worker ID %', worker_id;
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error processing worker shifts: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;
```

**הוכחת הפעלה:**
![Screenshot 2025-06-10 125017](https://github.com/user-attachments/assets/8e96ae9e-bfcc-4c7b-beeb-311fbd0821d6)

הפונקציה הופעלה בהצלחה עבור עובד מזהה 6 (Oriana Emlen) והחזירה:
- **שם עובד:** Oriana Emlen
- **סה"כ משמרות:** 48
- **סה"כ שעות:** 382.67
- **שעות נוספות:** 2.75
- **שכר מוערך:** $5,760.62

---

### פונקציה 2: `get_equipment_maintenance_status`

**תיאור מילולי:**
פונקציה המחזירה Ref Cursor עם מידע מפורט על סטטוס תחזוקת ציוד. הפונקציה מצרפת נתונים מטבלאות ציוד, תחזוקה וחוזים, ומחשבת מצב אחריות, מספר תחזוקות ועלויות כוללות.

**קוד הפונקציה:**
```sql
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
```

**הוכחת הפעלה:**
![Screenshot 2025-06-10 125909](https://github.com/user-attachments/assets/cb1e3f85-94a3-4a8d-bc84-bf835fca117f)

הפונקציה הופעלה בהצלחה והחזירה ref cursor עם מידע על ציוד, כולל מצב אחריות ונתוני תחזוקה.

---

## פרוצדורות (Procedures)

### פרוצדורה 1: `update_worker_contract`

**תיאור מילולי:**
פרוצדורה לעדכון פרטי חוזה עובד, כולל תפקיד, סוג חוזה והעלאת שכר. הפרוצדורה מבצעת אימות קיום העובד, מעדכנת את הנתונים בטבלאות הרלוונטיות (hourly/monthly), ומבצעת COMMIT או ROLLBACK בהתאם להצלחה.

**קוד הפרוצדורה:**
```sql
CREATE OR REPLACE PROCEDURE update_worker_contract(
    IN p_worker_id INTEGER,
    IN p_new_job_title TEXT,
    IN p_new_contract TEXT,
    IN p_wage_increase NUMERIC DEFAULT 0
)
LANGUAGE plpgsql AS $$
DECLARE
    worker_exists BOOLEAN := FALSE;
    current_wage NUMERIC;
    worker_type TEXT;
    worker_name TEXT;
BEGIN
    -- Check if worker exists and get their name
    SELECT TRUE, p.firstname || ' ' || p.lastname INTO worker_exists, worker_name
    FROM worker w
    JOIN person p ON w.pid = p.pid
    WHERE w.pid = p_worker_id;
    
    IF NOT worker_exists THEN
        RAISE EXCEPTION 'Worker with ID % does not exist', p_worker_id;
    END IF;
    
    -- Update worker information
    UPDATE worker 
    SET job = p_new_job_title,
        contract = p_new_contract
    WHERE pid = p_worker_id;
    
    -- Check if worker is hourly and update wage
    IF EXISTS (SELECT 1 FROM hourly WHERE pid = p_worker_id) THEN
        SELECT salaryph INTO current_wage FROM hourly WHERE pid = p_worker_id;
        
        UPDATE hourly 
        SET salaryph = current_wage + p_wage_increase
        WHERE pid = p_worker_id;
        
        worker_type := 'HOURLY';
        current_wage := current_wage + p_wage_increase;
    ELSIF EXISTS (SELECT 1 FROM monthly WHERE pid = p_worker_id) THEN
        SELECT "salaryPM" INTO current_wage FROM monthly WHERE pid = p_worker_id;
        
        UPDATE monthly 
        SET "salaryPM" = current_wage + p_wage_increase
        WHERE pid = p_worker_id;
        
        worker_type := 'MONTHLY';
        current_wage := current_wage + p_wage_increase;
    ELSE
        worker_type := 'NO_WAGE_INFO';
        current_wage := 0;
    END IF;
    
    RAISE NOTICE 'SUCCESS: Worker % (%) contract updated!', worker_name, p_worker_id;
    RAISE NOTICE '  New Job: %', p_new_job_title;
    RAISE NOTICE '  New Contract: %', p_new_contract;
    RAISE NOTICE '  Worker Type: %', worker_type;
    RAISE NOTICE '  New Wage: $%', current_wage;
    
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE EXCEPTION 'Error updating worker contract: %', SQLERRM;
END;
$$;
```

**הוכחת הפעלה:**
![Screenshot 2025-06-10 130215](https://github.com/user-attachments/assets/0f7af003-6933-4368-afb8-7421f113a0dd)

הפרוצדורה הופעלה בהצלחה ועדכנה את חוזה העובד עם הודעות מפורטות על השינויים שבוצעו.

---

### פרוצדורה 2: `process_equipment_orders`

**תיאור מילולי:**
פרוצדורה לעיבוד הזמנות ציוד מספק מסוים. הפרוצדורה משתמשת בmachוון לעבור על ההזמנות, מחשבת עלויות לפי קטגוריית ציוד, ומספקת סיכום מפורט של ההזמנות שעובדו.

**קוד הפרוצדורה:**
```sql
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
    
    order_cursor CURSOR FOR
        SELECT es.equipment_id, es.quantity, es.supply_date, e.name, e.category
        FROM equipment_supplier es
        JOIN equipment e ON es.equipment_id = e.equipment_id
        WHERE es.pid = p_supplier_id 
        AND es.supply_date >= p_order_date
        ORDER BY es.supply_date;
BEGIN
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
    
    FOR order_rec IN order_cursor LOOP
        BEGIN
            DECLARE
                item_cost NUMERIC;
                base_price NUMERIC;
            BEGIN
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
                            order_count, order_rec.quantity, order_rec.name, order_rec.equipment_id;
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
```

**הוכחת הפעלה:**
![Screenshot 2025-06-10 130818](https://github.com/user-attachments/assets/c4be63bc-5ba2-4403-a238-b7c86c68db19)

הפרוצדורה הופעלה בהצלחה ועיבדה הזמנות ציוד עם חישובי עלויות מפורטים.

---

## טריגרים (Triggers)

### טריגר 1: `worker_shift_validation_trigger`

**תיאור מילולי:**
טריגר המאמת נתוני משמרות עובדים לפני הכנסה או עדכון. הטריגר בודק זמני משמרת תקינים, מונע חפיפות במשמרות, ומוודא אורך משמרת סביר (1-16 שעות).

**קוד הטריגר:**
```sql
CREATE OR REPLACE FUNCTION validate_worker_shift()
RETURNS TRIGGER AS $$
DECLARE
    overlap_count INTEGER;
    shift_hours NUMERIC;
BEGIN
    shift_hours := EXTRACT(EPOCH FROM (NEW.clock_out - NEW.clock_in)) / 3600;
    
    IF NEW.clock_in >= NEW.clock_out THEN
        RAISE EXCEPTION 'Invalid shift times: clock_in (%) must be before clock_out (%)', 
                       NEW.clock_in, NEW.clock_out;
    END IF;
    
    IF shift_hours > 16 THEN
        RAISE EXCEPTION 'Shift too long: % hours. Maximum 16 hours allowed', 
                       ROUND(shift_hours, 2);
    END IF;
    
    IF shift_hours < 1 THEN
        RAISE EXCEPTION 'Shift too short: % hours. Minimum 1 hour required', 
                       ROUND(shift_hours, 2);
    END IF;
    
    SELECT COUNT(*) INTO overlap_count
    FROM shift s
    WHERE s.pid = NEW.pid
    AND s.date = NEW.date
    AND s.clock_in < NEW.clock_out
    AND s.clock_out > NEW.clock_in
    AND (TG_OP = 'INSERT' OR s.pid != OLD.pid OR s.date != OLD.date);
    
    IF overlap_count > 0 THEN
        RAISE EXCEPTION 'Shift overlap detected for worker % on %: % - %', 
                       NEW.pid, NEW.date, NEW.clock_in, NEW.clock_out;
    END IF;
    
    RAISE NOTICE 'Shift validated for worker %: % hours on %', 
                 NEW.pid, ROUND(shift_hours, 2), NEW.date;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER worker_shift_validation_trigger
    BEFORE INSERT OR UPDATE ON shift
    FOR EACH ROW
    EXECUTE FUNCTION validate_worker_shift();
```

**הוכחת הפעלה:**
![Screenshot 2025-06-10 131217](https://github.com/user-attachments/assets/4e1f82f2-d7f5-4bf9-84af-fd920a1870af)

![Screenshot 2025-06-10 131240](https://github.com/user-attachments/assets/985e44b7-eddb-485e-8d9d-de188a78f448)

הטריגר עבד בהצלחה וזרק שגיאה כאשר ניסינו להכניס משמרת לא תקינה (clock_out לפני clock_in).

---

### טריגר 2: `equipment_validation_trigger`

**תיאור מילולי:**
טריגר המאמת נתוני ציוד לפני הכנסה או עדכון. הטריגר בודק קטגוריות ציוד תקינות, תאריכי רכישה ואחריות הגיוניים, ומוודא שמות ציוד לא ריקים.

**קוד הטריגר:**
```sql
CREATE OR REPLACE FUNCTION validate_equipment_data()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.category NOT IN ('Strength', 'Cardio', 'Flexibility') THEN
        RAISE EXCEPTION 'Invalid equipment category: %. Allowed categories: Strength, Cardio, Flexibility', 
                       NEW.category;
    END IF;
    
    IF NEW.purchase_date > CURRENT_DATE THEN
        RAISE EXCEPTION 'Invalid purchase date: % cannot be in the future', NEW.purchase_date;
    END IF;
    
    IF NEW.warranty_expiry < NEW.purchase_date THEN
        RAISE EXCEPTION 'Invalid warranty: expiry date (%) cannot be before purchase date (%)', 
                       NEW.warranty_expiry, NEW.purchase_date;
    END IF;
    
    IF NEW.name IS NULL OR TRIM(NEW.name) = '' THEN
        RAISE EXCEPTION 'Equipment name cannot be empty';
    END IF;
    
    RAISE NOTICE 'Equipment validated: % (%) - Category: %', 
                 NEW.name, NEW.equipment_id, NEW.category;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER equipment_validation_trigger
    BEFORE INSERT OR UPDATE ON equipment
    FOR EACH ROW
    EXECUTE FUNCTION validate_equipment_data();
```

**הוכחת הפעלה:**
![Screenshot 2025-06-10 131450](https://github.com/user-attachments/assets/2d1ff4d9-741e-47e4-bf5e-7d9341db9a4a)

![Screenshot 2025-06-10 131502](https://github.com/user-attachments/assets/6b44943b-8dee-4e7b-b1b2-dda48a4e25c3)


הטריגר עבד בהצלחה ומנע הכנסת ציוד עם קטגוריה לא תקינה.

---

## תוכניות ראשיות (Main Programs)

### תוכנית ראשית 1: `main1_worker_management`

**תיאור מילולי:**
תוכנית ראשית המשלבת את פונקציה 1 ופרוצדורה 1 למערכת ניהול עובדים מקיפה. התוכנית מקבלת סיכום משמרות עובד ומעדכנת את חוזה העבודה שלו.

**קוד התוכנית:**
```sql
DO $$
DECLARE
    worker_summary RECORD;
    selected_worker_id INTEGER := 6;
BEGIN
    RAISE NOTICE '=== WORKER MANAGEMENT SYSTEM ===';
    RAISE NOTICE 'Date: %', CURRENT_DATE;
    RAISE NOTICE '=====================================';
    
    RAISE NOTICE 'Step 1: Getting shift summary for worker ID: %', selected_worker_id;
    
    BEGIN
        SELECT * INTO worker_summary 
        FROM get_worker_shift_summary(selected_worker_id);
        
        RAISE NOTICE 'SHIFT SUMMARY RESULTS:';
        RAISE NOTICE '  Worker Name: %', worker_summary.worker_name;
        RAISE NOTICE '  Total Shifts: %', worker_summary.total_shifts;
        RAISE NOTICE '  Total Hours: %', ROUND(worker_summary.total_hours, 2);
        RAISE NOTICE '  Overtime Hours: %', ROUND(worker_summary.overtime_hours, 2);
        RAISE NOTICE '  Estimated Pay: $%', ROUND(worker_summary.total_pay, 2);
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Error getting worker summary: %', SQLERRM;
    END;
    
    RAISE NOTICE '';
    RAISE NOTICE 'Step 2: Updating worker contract...';
    
    BEGIN
        CALL update_worker_contract(
            selected_worker_id,
            'Lead Fitness Coordinator',
            'Full-time Premium Plus',
            3.75
        );
        
        RAISE NOTICE 'Worker contract update completed successfully!';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Error updating worker contract: %', SQLERRM;
    END;
    
    RAISE NOTICE '';
    RAISE NOTICE '=== WORKER MANAGEMENT COMPLETED ===';
END;
$$;
```

**הוכחת הפעלה:**
![Screenshot 2025-06-10 131604](https://github.com/user-attachments/assets/9f6b825a-5e50-4a72-8e16-3858e1bce731)

התוכנית הופעלה בהצלחה, הציגה סיכום משמרות מפורט ועדכנה את חוזה העובד.

---

### תוכנית ראשית 2: `main2_equipment_management`

**תיאור מילולי:**
תוכנית ראשית המשלבת את פונקציה 2 ופרוצדורה 2 למערכת ניהול ציוד והזמנות. התוכנית מציגה דוח מצב ציוד ומעבדת הזמנות מספק.

**קוד התוכנית:**
```sql
DO $$
DECLARE
    equipment_cursor REFCURSOR;
    equipment_rec RECORD;
    supplier_id INTEGER := 1311;
    record_count INTEGER := 0;
BEGIN
    RAISE NOTICE '=== EQUIPMENT AND MAINTENANCE SYSTEM ===';
    RAISE NOTICE 'Date: %', CURRENT_DATE;
    RAISE NOTICE '==========================================';
    
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
```

**הוכחת הפעלה:**
![Screenshot 2025-06-10 131644](https://github.com/user-attachments/assets/4b38e036-893c-4836-b0d8-bc2fef7239a6)

התוכנית הופעלה בהצלחה, הציגה דוח ציוד מפורט ועיבדה הזמנות מספק.

---

## קבצים שהועלו לגיט

### קבצי תוכנה:
* **function1_worker_shifts.sql** – פונקציית חישוב סיכום משמרות עובדים
* **function2_equipment_status.sql** – פונקציית דוח מצב ותחזוקת ציוד  
* **procedure1_update_contract.sql** – פרוצדורת עדכון חוזי עובדים
* **procedure2_process_orders.sql** – פרוצדורת עיבוד הזמנות ציוד
* **trigger1_shift_validation.sql** – טריגר אימות משמרות עובדים
* **trigger2_equipment_validation.sql** – טריגר אימות נתוני ציוד
* **main1_worker_management.sql** – תוכנית ראשית לניהול עובדים
* **main2_equipment_management.sql** – תוכנית ראשית לניהול ציוד

### קבצי תיעוד ותמיכה:
* **backup4.sql** – גיבוי מסד הנתונים אחרי שלב ד
* **README.md** – דוח מפורט זה

### תכונות מתקדמות שיושמו:
---

### סיכום ביצועים:
כל הרכיבים נבדקו בהצלחה ומדגימים יכולות PL/pgSQL מתקדמות לניהול מערכת מכון ספורטיבי מקצועית. המערכת מספקת פתרונות עסקיים מלאים לניהול עובדים, ציוד, הזמנות ותחזוקה.
