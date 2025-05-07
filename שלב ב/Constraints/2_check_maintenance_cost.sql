-- 2_check_maintenance_cost.sql
-- CHECK constraint: maintenance.cost must be non-negative
ALTER TABLE maintenance
ADD CONSTRAINT chk_maintenance_cost_positive
CHECK (cost >= 0);
