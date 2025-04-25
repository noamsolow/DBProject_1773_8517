-- טבלת ספקים
INSERT INTO Supplier (name, contact_number, email, address) VALUES 
('GymTech Ltd.', '050-1234567', 'contact@gymtech.com', 'Herzliya 5, IL'),
('FitEquip Co.', '052-7654321', 'sales@fitequip.com', 'Haifa 22, IL'),
('ProFit Supply', '053-1122334', 'support@profit.com', 'Tel Aviv 99, IL');

-- טבלת ציוד
INSERT INTO Equipment (name, category, purchase_date, warranty_expiry, brand) VALUES 
('Treadmill X100', 'Cardio', '2023-01-15', '2025-01-15', 'TechRun'),
('Bench Press', 'Strength', '2022-05-10', '2024-05-10', 'IronFit'),
('Stretch Bands Set', 'Flexibility', '2023-03-20', '2024-03-20', 'FlexPro');

-- טבלת תחזוקה
INSERT INTO Maintenance (equipment_id, service_date, nextService_date, technician_name, description, cost) VALUES 
(1, '2024-01-01', '2024-06-01', 'David Levi', 'Routine maintenance', 150.00),
(2, '2024-02-15', '2024-08-15', 'Sarah Cohen', 'Replaced cable', 250.00),
(3, '2024-03-10', '2024-09-10', 'Moshe Ben', 'Cleaned and tested', 90.00);

-- ציוד אירובי
INSERT INTO CardioEquipment (equipment_id, incline_levels, has_heart_rate_monitor, max_speed) VALUES 
(1, 12, TRUE, 18.5);

-- ציוד כוח
INSERT INTO StrengthEquipment (equipment_id, adjustable, resistance_type, max_weight) VALUES 
(2, TRUE, 'Plate Loaded', 150.00);

-- ציוד גמישות
INSERT INTO FlexibilityEquipment (equipment_id, portable, length_cm, material) VALUES 
(3, TRUE, 200, 'Rubber');

-- קשר בין ספקים לציוד
INSERT INTO Equipment_Supplier (equipment_id, supplier_id, quantity, supply_date) VALUES 
(1, 1, 5, '2023-01-10'),
(2, 2, 2, '2022-05-01'),
(3, 3, 10, '2023-03-15');
