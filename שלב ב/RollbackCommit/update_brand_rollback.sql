-- Start a transaction
BEGIN;

-- Perform an update (for example, update the brand of some equipment)
UPDATE Equipment
SET brand = 'Life Fitness 4ever' 
WHERE brand = 'Life Fitness'

-- Rollback the transaction to undo the changes
ROLLBACK;