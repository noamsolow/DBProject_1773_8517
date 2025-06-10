-- Trigger 1: Worker shift validation
CREATE OR REPLACE FUNCTION validate_worker_shift()
RETURNS TRIGGER AS $$
DECLARE
    overlap_count INTEGER;
    shift_hours NUMERIC;
BEGIN
    -- Calculate shift hours
    shift_hours := EXTRACT(EPOCH FROM (NEW.clock_out - NEW.clock_in)) / 3600;
    
    -- Validate shift times
    IF NEW.clock_in >= NEW.clock_out THEN
        RAISE EXCEPTION 'Invalid shift times: clock_in (%) must be before clock_out (%)', 
                       NEW.clock_in, NEW.clock_out;
    END IF;
    
    -- Check for reasonable shift length (max 16 hours, min 1 hour)
    IF shift_hours > 16 THEN
        RAISE EXCEPTION 'Shift too long: % hours. Maximum 16 hours allowed', 
                       ROUND(shift_hours, 2);
    END IF;
    
    IF shift_hours < 1 THEN
        RAISE EXCEPTION 'Shift too short: % hours. Minimum 1 hour required', 
                       ROUND(shift_hours, 2);
    END IF;
    
    -- Check for overlapping shifts for the same worker on the same date
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
    
    -- Success message
    RAISE NOTICE 'Shift validated for worker %: % hours on %', 
                 NEW.pid, ROUND(shift_hours, 2), NEW.date;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger
CREATE TRIGGER worker_shift_validation_trigger
    BEFORE INSERT OR UPDATE ON shift
    FOR EACH ROW
    EXECUTE FUNCTION validate_worker_shift();