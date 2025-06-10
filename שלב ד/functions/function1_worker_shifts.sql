-- Function 1: Get worker shift summary (corrected for your schema)
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
    hourly_wage NUMERIC := 15.00; -- Default wage
    overtime_rate NUMERIC := 22.50; -- Default overtime rate
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
            -- Calculate hours for this shift
            shift_hours := EXTRACT(EPOCH FROM (shift_rec.clock_out - shift_rec.clock_in)) / 3600;
            
            total_shifts := total_shifts + 1;
            total_hours := total_hours + shift_hours;
            
            -- Calculate overtime (over 8 hours per shift)
            IF shift_hours > 8 THEN
                overtime_hours := overtime_hours + (shift_hours - 8);
            END IF;
        END;
    END LOOP;
    CLOSE shift_cursor;
    
    -- Calculate total pay
    total_pay := (total_hours - overtime_hours) * hourly_wage + 
                 overtime_hours * overtime_rate;
    
    -- Set the return value
    worker_name := worker_full_name;
    
    RETURN NEXT;
    
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RAISE EXCEPTION 'No data found for worker ID %', worker_id;
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error processing worker shifts: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;