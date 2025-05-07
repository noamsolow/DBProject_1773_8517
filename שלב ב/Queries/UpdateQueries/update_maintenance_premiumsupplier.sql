-- update_maintenance_premiumsupplier.sql
-- UPDATE: Increase maintenance cost by 10% for equipment supplied by PremiumSupplier
UPDATE maintenance AS m
SET cost = cost * 1.10
FROM equipment_supplier AS es
JOIN supplier AS s ON es.supplier_id = s.supplier_id
WHERE m.equipment_id = es.equipment_id
  AND s.name = 'PremiumSupplier';
