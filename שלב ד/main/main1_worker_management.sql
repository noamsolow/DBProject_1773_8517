-- Main Program 1: Worker Management System
DO $$
DECLARE
    worker_summary RECORD;
    selected_worker_id INTEGER := 6; -- Using worker 6 (Oriana Emlen)
BEGIN
    RAISE NOTICE '=== WORKER MANAGEMENT SYSTEM ===';
    RAISE NOTICE 'Date: %', CURRENT_DATE;
    RAISE NOTICE '=====================================';
    
    -- Call Function 1: Get worker shift summary
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
    
    -- Call Procedure 1: Update worker contract
    BEGIN
        CALL update_worker_contract(
            selected_worker_id,
            'Lead Fitness Coordinator',
            'Full-time Premium Plus',
            3.75 -- $3.75 wage increase
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