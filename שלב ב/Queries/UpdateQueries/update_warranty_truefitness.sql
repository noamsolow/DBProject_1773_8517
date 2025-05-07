-- update_warranty_truefitness.sql
-- UPDATE: Advance warranty_expiry by one month for strength equipment from True Fitness
UPDATE equipment AS e
SET warranty_expiry = warranty_expiry - INTERVAL '1 month'
FROM strengthequipment AS se
WHERE e.equipment_id = se.equipment_id
  AND e.brand = 'True Fitness';
