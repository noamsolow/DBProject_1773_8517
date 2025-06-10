-- Procedure 1: Update worker contract information (FIXED with correct column names)
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
        
    -- Check if worker is monthly and update wage
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
    
    -- Log the update
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