# דוח פרויקט - שלב ג'

## תוכן עניינים

1. [תרשימי ERD ו-DSD](#תרשימי-erd-ו-dsd)
2. [החלטות בשלב האינטגרציה](#החלטות-בשלב-האינטגרציה)
3. [פקודות SQL עיקריות (Integrate.sql)](#פקודות-sql-עיקריות-integratesql)
4. [מבטי View ושאילתות לדוגמה (Views.sql)](#מבטי-view-ושאילתות-לדוגמה-viewssql)
5. [קבצים שהועלו לגיט](#קבצים)

## תרשימי ERD ו-DSD

הנה הגרסה ללא אימוג'ים, בפורמט מסודר כמו שצריך לדוח או README:

---

## Equipment

### ERD – תרשים ישויות קשרים

![equipment](https://github.com/user-attachments/assets/8d4eb224-fa35-4f62-8155-6cb5bc549d8b)

### DSD – תרשים מבנה נתונים

![equipment_schema](https://github.com/user-attachments/assets/c4edd8f8-b723-4f3c-a102-bd37bb868519)

---

## Gym People

### ERD – תרשים ישויות קשרים

![gym_people](https://github.com/user-attachments/assets/7172bc58-1b38-4442-8c40-6be7f1e0669f)

### DSD – תרשים מבנה נתונים

![gym_people_schema](https://github.com/user-attachments/assets/e8ebac78-9ee1-48fc-a534-830e552f484f)

---

## Combined

### ERD – תרשים ישויות קשרים משולב

![combined_erd](https://github.com/user-attachments/assets/1028a409-c426-4eb6-9aa6-edd6d78096b0)

### DSD – תרשים מבנה נתונים משולב

![combined_schema](https://github.com/user-attachments/assets/1bb28a70-28e6-4e93-8ae6-7c6fc17d9edf)

---



## החלטות בשלב האינטגרציה
---
 **איחוד הגורמים האנושיים**
   כל היישויות Freelancer, Supplier ו־Worker אוחדו כישויות ילד של הטבלה המרכזית person, תוך שמירה על תתי-טבלאות נפרדות (Freelancer, Supplier) כהרחבות (subtypes) מבוססות pId.


 **יצירת טבלת על חוזים (Contract\_job)**
   הוקמה טבלה חדשה בשם Contract_job שמאגדת לתוכה את כלל החוזים: גם שירותים (serves) וגם תחזוקות (maintenance). טבלה זו מהווה את הליבה של כל פעולת שירות במערכת המאוחדת.


**מניעת התנגשות מזהים**
   מאחר והטבלה Supplier כללה מזהים שעלולים להתנגש עם מזהי person, בוצע עדכון של כל supplier_id במסד הנתונים – והם הוגדלו ב־1000.


**הקמה ושינוי של תתי-טבלאות**
   טבלאות המשנה Freelancer ו־Supplier הוגדרו מחדש כך שכל אחת מהן מקבלת את pId שלה מ־person, בהתאם לעיקרון היררכיה טיפוסית.


**הגדרת טבלת Maintenance חדשה**
   הטבלה Maintenance החדשה קושרת בין ציוד (equipment) לבין חוזה (Contract_job) ומייצגת קשר 1:1 לתחזוקה בפועל, תוך שמירה על נורמליזציה.


**העברת נתונים מלאה**
   בוצעה מיגרציה מסודרת של כל הנתונים מהטבלאות הישנות: maintenance_old, freelancer, serves_backup לתוך המבנה החדש. הנתונים שומרו בסדר ובקשר נכון, כולל התאמה בין מזהים.


**ניקוי טבלאות ישנות**
   לאחר קליטת המידע, בוצע ניקוי מלא (DROP) של טבלאות ישנות ומיותרות – כולל freelancer, maintenance_old ו־serves.

**עדכון טבלת השירותים (services)**
   הערך 'supplier' הוסר מטבלת השירותים, מאחר שספקים אינם מספקים שירות ישיר אלא מהווים ישות אנושית (person) ואינם מייצגים קטגוריית שירות לגיטימית. במקביל, נוסף שירות חדש 'maintenance' לטבלת services, כדי לאפשר תיעוד תחזוקות כחלק מהשירותים הניתנים במערכת המאוחדת.
   

## פקודות SQL עיקריות (Integrate.sql)

* **עדכון מזהים לספקים למניעת התנגשויות עם מזהי `person`:**

```sql
UPDATE Supplier SET supplier_id = supplier_id + 1000;
UPDATE equipment_supplier SET supplier_id = supplier_id + 1000;
```

* **הכנסת ספקים לטבלת `person` עם ערכי ברירת מחדל:**

```sql
INSERT INTO person (pId, dateofb, firstname, lastname, email, address, phone)
SELECT supplier_id, DATE '1900-01-01', 'Supplier', '', email, address,
       regexp_replace(contact_number, '\\D', '', 'g')::numeric
FROM Supplier;
```

* **הגדרת תת-טבלה Supplier כממשיכה של `person`:**

```sql
INSERT INTO Supplier (pId)
SELECT supplier_id FROM Supplier;
```

* **התאמת `equipment_supplier` למבנה החדש:**

```sql
ALTER TABLE equipment_supplier RENAME COLUMN supplier_id TO pId;
ALTER TABLE equipment_supplier ADD CONSTRAINT fk_equipment_supplier_person FOREIGN KEY (pId) REFERENCES person(pId);
```

* **שימור נתוני התחזוקה הישנים בטבלה זמנית:**

```sql
ALTER TABLE maintenance RENAME TO maintenance_old;
```

* **יצירת טבלת חוזים מאוחדת `Contract_job`:**

```sql
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
```

* **העברת רשומות תחזוקה ישנות לטבלת חוזים חדשה:**

```sql
INSERT INTO Contract_job (pId, service_name, cost, service_date, estimated_next_service, description)
SELECT 9999, 'maintenance', cost, service_date, nextService_date, description FROM maintenance_old;
```

* **יצירת טבלה חדשה לתחזוקה המקשרת בין חוזים לציוד:**

```sql
CREATE TABLE Maintenance_new (
    contract_id INT PRIMARY KEY REFERENCES Contract_job(contract_id),
    equipment_id INT REFERENCES Equipment(equipment_id)
);
```

* **חיבור לפי סדר שורות בין ציוד לחוזי תחזוקה:**

```sql
WITH contract_rows AS (
    SELECT contract_id, ROW_NUMBER() OVER () AS row_num FROM Contract_job WHERE service_name = 'maintenance'
),
equipment_rows AS (
    SELECT equipment_id, ROW_NUMBER() OVER () AS row_num FROM maintenance_old
)
INSERT INTO Maintenance_new (contract_id, equipment_id)
SELECT c.contract_id, e.equipment_id
FROM contract_rows c JOIN equipment_rows e ON c.row_num = e.row_num;
```

* **מחיקת טבלאות ישנות לאחר ההעברה:**

```sql
DROP TABLE IF EXISTS serves;
DROP TABLE IF EXISTS maintenance_old;
```

* **שינוי שם הטבלה החדשה לתחזוקה:**

```sql
ALTER TABLE Maintenance_new RENAME TO Maintenance;
```

* **הוספת נתוני שירות ישנים (serves) למודל החדש:**

```sql
INSERT INTO Contract_job (pId, service_name, cost, service_date, estimated_next_service, description, contract)
SELECT pId, service_name, price, service_date_begin, service_end_date, 'description', contract FROM serves_backup;
```

* **החלפת ערך 'supplier' בשירותים אקראיים אמיתיים:**

```sql
UPDATE Contract_job
SET service_name = CASE FLOOR(RANDOM() * 4)
    WHEN 0 THEN 'plumber'
    WHEN 1 THEN 'painter'
    WHEN 2 THEN 'electrician'
    WHEN 3 THEN 'handy man'
END
WHERE service_name = 'supplier';
```

* **מחיקת השירות הלא תקני 'supplier' ממילון השירותים:**

```sql
DELETE FROM services WHERE service_name = 'supplier';
```

* **הוספת שירות חדש 'maintenance' במידת הצורך:**

```sql
INSERT INTO services (service_name, equipmentrequired)
VALUES ('maintenance', 'Equipment0')
ON CONFLICT DO NOTHING;
```
---

## מבטי View ושאילתות לדוגמה (Views.sql)


### מבט 1: `equipment_maintenance_view`

**קוד יצירת המבט:**

```sql
CREATE VIEW equipment_maintenance_view AS
SELECT 
    m.contract_id,
    e.equipment_id,
    e.name AS equipment_name,
    cj.service_date,
    cj.estimated_next_service,
    cj.cost,
    cj.description
FROM Maintenance m
JOIN Equipment e ON m.equipment_id = e.equipment_id
JOIN Contract_job cj ON m.contract_id = cj.contract_id
WHERE cj.service_name = 'maintenance';
```

**תיאור:**
מציג מידע על פעולות תחזוקה שבוצעו בציוד, כולל תאריך, עלות, תיאור ושם הציוד.

**שאילתת SELECT \* לדוגמה:**

```sql
SELECT * FROM equipment_maintenance_view LIMIT 10;
```

*תמונה לדוגמה:*
![Screenshot 2025-05-21 230248](https://github.com/user-attachments/assets/22b2a1ed-1e6e-4bb9-ab0a-40ba5d7d5fc6)

**שאילתה 1:** מהם חמשת הציודים שעברו הכי הרבה תחזוקות?

```sql
SELECT equipment_name, COUNT(*) AS maintenance_count
FROM equipment_maintenance_view
GROUP BY equipment_name
ORDER BY maintenance_count DESC
LIMIT 5;
```

**הסבר:**
מאפשר לזהות ציוד שמקולקל או דורש תחזוקה תכופה.

*תמונה לדוגמה:*
![Screenshot 2025-05-21 230358](https://github.com/user-attachments/assets/a4d66fb2-79e7-4cfd-b7f5-71e7e35fcc90)

**שאילתה 2:** כמה כסף הוצא על תחזוקה בכל יום?

```sql
SELECT service_date, SUM(cost) AS total_cost
FROM equipment_maintenance_view
GROUP BY service_date
ORDER BY service_date;
```

**הסבר:**
לצורך ניתוח תקציבי של הוצאות תחזוקה לפי תאריכים.

*תמונה לדוגמה:*
![Screenshot 2025-05-21 230416](https://github.com/user-attachments/assets/94fbd618-6b9c-4a14-a757-eb87b76a897f)

---

### מבט 2: `freelancer_services_view`

**קוד יצירת המבט:**

```sql
CREATE VIEW freelancer_services_view AS
SELECT 
    f.pId,
    p.firstname || ' ' || p.lastname AS full_name,
    cj.service_name,
    cj.service_date,
    cj.estimated_next_service,
    cj.cost
FROM freelancer f
JOIN person p ON f.pId = p.pId
JOIN Contract_job cj ON f.pId = cj.pId;
```

**תיאור:**
מציג עבור כל פרילנסר את השירותים שביצע, כולל שם מלא, סוג שירות, עלות ותאריכים.

**שאילתת SELECT \* לדוגמה:**

```sql
SELECT * FROM freelancer_services_view LIMIT 10;
```

*תמונה לדוגמה:*
![Screenshot 2025-05-21 230304](https://github.com/user-attachments/assets/43a57117-948e-4432-b4fc-293427538ae8)

**שאילתה 1:** כמה שירותים ביצע כל פרילנסר?

```sql
SELECT full_name, COUNT(*) AS service_count
FROM freelancer_services_view
GROUP BY full_name
ORDER BY service_count DESC;
```

**הסבר:**
ניתוח תפוקת עבודה של פרילנסרים.

*תמונה לדוגמה:*
![Screenshot 2025-05-21 230430](https://github.com/user-attachments/assets/ccf69309-adc0-420c-86eb-2fcb60f73130)

**שאילתה 2:** מהי העלות הממוצעת לפי סוג שירות?

```sql
SELECT service_name, AVG(cost) AS avg_cost
FROM freelancer_services_view
GROUP BY service_name
ORDER BY avg_cost DESC;
```

**הסבר:**
מטרת השאילתה היא להבין אילו שירותים הם היקרים ביותר.

*תמונה לדוגמה:*
![Screenshot 2025-05-21 230445](https://github.com/user-attachments/assets/225b1596-3df7-4d85-87eb-1e9a1322a33f)

---


## קבצים


---


* **backup** – תיקיית גיבויים כלליים שנשמרו במהלך העבודה.
* **combined_ERD_DSD** – קבצי ERD ו-DSD המשולבים לאחר האינטגרציה הסופית.
* **gym_people_ERD_DSD** – דיאגרמות ישויות-קשרים ומבנה נתונים עבור תת-המערכת של האנשים במכון.
* **original_ERD_DSD** – הקבצים המקוריים של ERD ו-DSD טרם השלב האינטגרטיבי.
* **Integrate.sql** – קובץ שמכיל את פעולות האינטגרציה בין הסכמות: `ALTER`, `INSERT`, `UPDATE`, ויצירת טבלאות חדשות.
* **Views.sql** – קובץ בו מרוכזים כל ה-Views שנוצרו לצרכי ניתוח, כולל שאילתות לדוגמה.
* **README.md** – דוח טקסטואלי זה, הכולל הסברים, החלטות עיצוביות, וקוד רלוונטי.

---

