-- Start a transaction
BEGIN;

-- Update Strength Equipment max_weight to be rounded 
UPDATE StrengthEquipment
SET max_weight = ROUND(max_weight);  

-- Commit the transaction to save the changes
COMMIT;
