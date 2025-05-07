-- 3_default_equipment_purchase_date.sql
-- DEFAULT constraint: set default purchase_date to current date
ALTER TABLE equipment
ALTER COLUMN purchase_date SET DEFAULT CURRENT_DATE;
