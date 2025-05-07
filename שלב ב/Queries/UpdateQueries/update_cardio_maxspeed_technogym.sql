-- update_cardio_maxspeed_technogym.sql
-- UPDATE: Increase max_speed by 10% for cardio equipment manufactured by Technogym
UPDATE cardioequipment AS ce
SET max_speed = max_speed * 1.10
FROM equipment AS e
WHERE ce.equipment_id = e.equipment_id
  AND e.brand = 'Technogym';
