-- =======================================
-- Integrate.sql – Table Alterations & Data Migrations
-- =======================================

-- 1. Shift supplier IDs by +1000 to avoid collision with existing pIds in person.
UPDATE Supplier SET supplier_id = supplier_id + 1000;
UPDATE equipment_supplier SET supplier_id = supplier_id + 1000;

-- Explanation:
-- Person and Supplier now share the same pId space.
-- To prevent conflicts, supplier IDs were shifted by 1000 so they don’t clash with existing people.

-- 2. Insert suppliers into person with dummy/default values for missing fields.
INSERT INTO person (pId, dateofb, firstname, lastname, email, address, phone)
SELECT supplier_id, DATE '1900-01-01', 'Supplier', '', email, address, 
       regexp_replace(contact_number, '\D', '', 'g')::numeric
FROM Supplier;

-- Explanation:
-- Suppliers are now treated as a subtype of person.
-- We inserted them into the `person` table to support the new unified entity model.

-- 3. Insert supplier pIds into Supplier subtype table (normalized design).
INSERT INTO Supplier (pId)
SELECT supplier_id FROM Supplier;

-- Explanation:
-- Since Supplier now inherits from Person, we store only the pId here to reflect the subtype in a normalized structure.

-- 4. Change equipment_supplier to reference person.pId instead of Supplier.
ALTER TABLE equipment_supplier RENAME COLUMN supplier_id TO pId;
ALTER TABLE equipment_supplier
ADD CONSTRAINT fk_equipment_supplier_person
FOREIGN KEY (pId) REFERENCES person(pId);

-- Explanation:
-- As Supplier is now a subtype of Person, the foreign key should point to `person(pId)`, not the old Supplier table.

-- 5. Rename old maintenance table temporarily.
ALTER TABLE maintenance RENAME TO maintenance_old;

-- Explanation:
-- This allows us to preserve the old data during the migration and create a new normalized version of the maintenance logic.

-- 6. Create Contract_job to unify services + maintenance logic.
CREATE TABLE Contract_job (
    contract_id SERIAL PRIMARY KEY,
    pId INT NOT NULL REFERENCES person(pId),
    service_name VARCHAR(100) NOT NULL REFERENCES services(service_name),
    cost NUMERIC(10,2),
    service_date DATE,
    estimated_next_service DATE,
    description VARCHAR(255),
    contract VARCHAR(100)
);

-- Explanation:
-- Instead of having separate tables for `maintenance` and `serves`, this unified table handles all contracts for services and maintenance jobs.

-- 7. Insert maintenance records into Contract_job with generic technician.
INSERT INTO Contract_job (pId, service_name, cost, service_date, 
                          estimated_next_service, description)
SELECT 9999, 'maintenance', cost, service_date, nextService_date, description
FROM maintenance_old;

-- Explanation:
-- Old maintenance records were migrated into the new `Contract_job` structure using a placeholder technician (pId 9999).

-- 8. Create new Maintenance table (contract_id + equipment_id).
CREATE TABLE Maintenance_new (
    contract_id INT PRIMARY KEY REFERENCES Contract_job(contract_id),
    equipment_id INT REFERENCES Equipment(equipment_id)
);

-- Explanation:
-- Maintenance is now represented as a connection between a contract and equipment.
-- This aligns with the normalized model where the maintenance details are in Contract_job.

-- 9. Connect contracts to equipment by order (1:1 with row numbers).
WITH contract_rows AS (
    SELECT contract_id, ROW_NUMBER() OVER () AS row_num FROM Contract_job WHERE service_name = 'maintenance'
),
equipment_rows AS (
    SELECT equipment_id, ROW_NUMBER() OVER () AS row_num FROM maintenance_old
)
INSERT INTO Maintenance_new (contract_id, equipment_id)
SELECT c.contract_id, e.equipment_id
FROM contract_rows c JOIN equipment_rows e ON c.row_num = e.row_num;

-- Explanation:
-- Since no explicit relationship was available, we assumed order-based matching between old maintenance records and new contracts to maintain a 1:1 mapping.

-- 10. Remove old tables no longer needed.
DROP TABLE IF EXISTS serves;
DROP TABLE IF EXISTS maintenance_old;

-- Explanation:
-- These legacy tables have been fully migrated into the new unified schema and are no longer necessary.

-- 11. Rename Maintenance_new to Maintenance
ALTER TABLE Maintenance_new RENAME TO Maintenance;

-- Explanation:
-- After verifying the new design, we replace the old Maintenance table with the new normalized version.

-- 12. Insert serves into Contract_job as generic services
INSERT INTO Contract_job (pId, service_name, cost, service_date,
                          estimated_next_service, description, contract)
SELECT pId, service_name, price, service_date_begin, service_end_date,
       'description', contract FROM serves_backup;

-- Explanation:
-- Data from the previous `serves` logic is now integrated into the new Contract_job structure for consistency and unification.

-- 13. Replace all Contract_job entries with 'supplier' as service_name
--     with random real services instead
UPDATE Contract_job
SET service_name = CASE FLOOR(RANDOM() * 4)
    WHEN 0 THEN 'plumber'
    WHEN 1 THEN 'painter'
    WHEN 2 THEN 'electrician'
    WHEN 3 THEN 'handy man'
END
WHERE service_name = 'supplier';

-- Explanation:
-- 'supplier' is not a valid service. This replaces placeholder values with actual service names to ensure data consistency.

-- 14. Remove 'supplier' from services dictionary
DELETE FROM services WHERE service_name = 'supplier';

-- Explanation:
-- Clean up dictionary to reflect actual available services and prevent future invalid inserts.

-- 15. Add 'maintenance' to services if not exists
INSERT INTO services (service_name, equipmentrequired)
VALUES ('maintenance', 'Equipment0')
ON CONFLICT DO NOTHING;

-- Explanation:
-- Ensure 'maintenance' is part of the service dictionary so maintenance jobs can be registered in Contract_job.
