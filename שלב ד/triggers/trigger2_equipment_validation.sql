-- Trigger 2: Equipment category and data validation
CREATE OR REPLACE FUNCTION validate_equipment_data()
RETURNS TRIGGER AS $$
BEGIN
    -- Validate category is one of allowed values
    IF NEW.category NOT IN ('Strength', 'Cardio', 'Flexibility') THEN
        RAISE EXCEPTION 'Invalid equipment category: %. Allowed categories: Strength, Cardio, Flexibility', 
                       NEW.category;
    END IF;
    
    -- Validate purchase date is not in the future
    IF NEW.purchase_date > CURRENT_DATE THEN
        RAISE EXCEPTION 'Invalid purchase date: % cannot be in the future', NEW.purchase_date;
    END IF;
    
    -- Validate warranty expiry is after purchase date
    IF NEW.warranty_expiry < NEW.purchase_date THEN
        RAISE EXCEPTION 'Invalid warranty: expiry date (%) cannot be before purchase date (%)', 
                       NEW.warranty_expiry, NEW.purchase_date;
    END IF;
    
    -- Validate equipment name is not empty
    IF NEW.name IS NULL OR TRIM(NEW.name) = '' THEN
        RAISE EXCEPTION 'Equipment name cannot be empty';
    END IF;
    
    -- Success message
    RAISE NOTICE 'Equipment validated: % (%) - Category: %', 
                 NEW.name, NEW.equipment_id, NEW.category;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger
CREATE TRIGGER equipment_validation_trigger
    BEFORE INSERT OR UPDATE ON equipment
    FOR EACH ROW
    EXECUTE FUNCTION validate_equipment_data();