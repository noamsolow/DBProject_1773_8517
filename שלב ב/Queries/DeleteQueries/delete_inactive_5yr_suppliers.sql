-- delete_inactive_5yr_suppliers.sql
-- DELETE: Remove suppliers with no deliveries in the last 5 years
DELETE FROM supplier AS s
WHERE NOT EXISTS (
  SELECT 1
  FROM equipment_supplier AS es
  WHERE es.supplier_id = s.supplier_id
    AND es.supply_date >= current_date - INTERVAL '5 years'
);
