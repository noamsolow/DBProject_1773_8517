-- delete_defective_bowflex.sql
-- DELETE: Remove all records for equipment from Bowflex

-- Delete from maintenance
DELETE FROM maintenance
WHERE equipment_id IN (
  SELECT e.equipment_id
  FROM equipment AS e
  WHERE e.brand = 'Bowflex'
);

-- Delete from equipment_supplier
DELETE FROM equipment_supplier
WHERE equipment_id IN (
  SELECT e.equipment_id
  FROM equipment AS e
  WHERE e.brand = 'Bowflex'
);

-- Delete from subtype tables
DELETE FROM cardioequipment
WHERE equipment_id IN (
  SELECT e.equipment_id
  FROM equipment AS e
  WHERE e.brand = 'Bowflex'
);
DELETE FROM strengthequipment
WHERE equipment_id IN (
  SELECT e.equipment_id
  FROM equipment AS e
  WHERE e.brand = 'Bowflex'
);
DELETE FROM flexibilityequipment
WHERE equipment_id IN (
  SELECT e.equipment_id
  FROM equipment AS e
  WHERE e.brand = 'Bowflex'
);

-- Finally, delete from equipment
DELETE FROM equipment
WHERE equipment_id IN (
  SELECT e.equipment_id
  FROM equipment AS e
  WHERE e.brand = 'Bowflex'
);
