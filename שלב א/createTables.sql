-- טבלת ספקים
CREATE TABLE Supplier (
    supplier_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    contact_number VARCHAR(20),
    email VARCHAR(100),
    address VARCHAR(255)
);

-- טבלת ציוד
CREATE TABLE Equipment (
    equipment_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    category VARCHAR(50),
    purchase_date DATE,
    warranty_expiry DATE,
    brand VARCHAR(50)
);

-- טבלת תחזוקה
CREATE TABLE Maintenance (
    maintenance_id SERIAL PRIMARY KEY,
    equipment_id INT,
    service_date DATE,
    nextService_date DATE,
    technician_name VARCHAR(100),
    description TEXT,
    cost NUMERIC(10,2),
    FOREIGN KEY (equipment_id) REFERENCES Equipment(equipment_id)
);

-- טבלת ציוד אירובי
CREATE TABLE CardioEquipment (
    equipment_id INT PRIMARY KEY,
    incline_levels INT,
    has_heart_rate_monitor BOOLEAN,
    max_speed NUMERIC(5,2),
    FOREIGN KEY (equipment_id) REFERENCES Equipment(equipment_id)
);

-- טבלת ציוד כוח
CREATE TABLE StrengthEquipment (
    equipment_id INT PRIMARY KEY,
    adjustable BOOLEAN,
    resistance_type VARCHAR(50),
    max_weight NUMERIC(6,2),
    FOREIGN KEY (equipment_id) REFERENCES Equipment(equipment_id)
);

-- טבלת ציוד גמישות
CREATE TABLE FlexibilityEquipment (
    equipment_id INT PRIMARY KEY,
    portable BOOLEAN,
    length_cm INT,
    material VARCHAR(50),
    FOREIGN KEY (equipment_id) REFERENCES Equipment(equipment_id)
);

-- טבלת קשר בין ספקים לציוד
CREATE TABLE Equipment_Supplier (
    equipment_id INT,
    supplier_id INT,
    quantity INT,
    supply_date DATE,
    PRIMARY KEY (equipment_id, supplier_id),
    FOREIGN KEY (equipment_id) REFERENCES Equipment(equipment_id),
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id)
);
