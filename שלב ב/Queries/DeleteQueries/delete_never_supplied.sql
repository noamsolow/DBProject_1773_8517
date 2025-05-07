-- delete_never_supplied.sql
-- DELETE: Remove suppliers who never supplied any equipment
DELETE FROM supplier AS s
WHERE NOT EXISTS (
  SELECT 1
  FROM equipment_supplier AS es
  WHERE es.supplier_id = s.supplier_id
);
