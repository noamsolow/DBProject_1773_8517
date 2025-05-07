-- 1_not_null_supplier_email.sql
-- NOT NULL constraint: supplier.email must not be null
ALTER TABLE supplier
ALTER COLUMN email SET NOT NULL;
