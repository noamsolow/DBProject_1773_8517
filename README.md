#  שלב ה' | מערכת ניהול מכון ספורט

## 📌 תוכן עניינים

1. [מבוא](#מבוא)
2. [רכיבי המערכת](#רכיבי-המערכת)
3. [תיאור הפעולה](#תיאור-הפעולה)
4. [שלבים להרצה](#שלבים-להרצה)
5. [מסכים עיקריים](#מסכים-עיקריים)
7. [קבצים במאגר](#קבצים-במאגר)

---

## מבוא

פרויקט זה מהווה את שלב ה' בפרויקט ניהול מכון הספורט. מטרתו היא בניית ממשק גרפי אינטראקטיבי המאפשר:

* **ביצוע CRUD** על ארבע טבלאות, כולל אחת מקשרת (junction table)
* **שילוב 4 שאילתות אנליטיות
* **הפעלת 2 פרוצדורות ו2 פונקציות** שנכתבו בשלב ד'

המערכת נבנתה ב־Python תוך שימוש ב־**Tkinter** כממשק GUI, ומתחברת למסד הנתונים PostgreSQL.

---

## רכיבי המערכת

* **שפת תכנות:** Python
* **GUI:** Tkinter
* **DBMS:** PostgreSQL
* **שכבות:**

  * ממשק משתמש
  * לוגיקה עסקית (קבצי operations)
  * חיבור למסד הנתונים (db\_manager)

---

## תיאור הפעולה

* המשתמש יכול לעבור בין מסכים לניהול:

  * עובדים (workers)
  * ספקים (suppliers)
  * ציוד (equipment)
  * ציוד מספקים (equipment\_supplier)

* ניתן להוסיף, לערוך ולמחוק רשומות בכל טבלה.

* במסכי העובדים והציוד שולבו אפשרויות חיפוש דינמי.

* הלחצנים במסך הראשי שולחים לאזורים הרלוונטיים, תוך ניהול content\_frame מרכזי.

---

## שלבים להרצה

1. להריץ את מסד הנתונים (למשל דרך pgAdmin או Docker)
2. לוודא שה־connection string בקובץ `database.py` מוגדר נכון
3. להריץ את הקובץ הראשי `main.py`
4. לבצע פעולות דרך ה־GUI (כמו הוספה, חיפוש ועדכון)

---

## מסכים עיקריים

### 🔹 דף ראשי
<img width="1493" height="1016" alt="image" src="https://github.com/user-attachments/assets/9785675e-2804-4d23-bd26-483808f673cc" />


### 🔹 ניהול עובדים

<img width="1495" height="1013" alt="image" src="https://github.com/user-attachments/assets/0bd4ccb1-be8e-48a4-b083-4304d0ef8a7b" />

### 🔹 ניהול ציוד

<img width="1493" height="1014" alt="image" src="https://github.com/user-attachments/assets/f50d1663-7d5a-4b56-a8a7-24c0163ea4aa" />

### 🔹 טבלת ספקים

<img width="1502" height="1016" alt="image" src="https://github.com/user-attachments/assets/2dc8c29e-d333-4a52-959a-a4b447d84d57" />

### 🔹 טבלת ציוד מספקים

<img width="1496" height="1019" alt="image" src="https://github.com/user-attachments/assets/73976dd2-d06d-4ac5-a655-746300d3292f" />

### 🔹 עמוד פונקציות ופרוצדורות

<img width="1499" height="1021" alt="image" src="https://github.com/user-attachments/assets/17294c75-aae7-4130-9193-f3e4b8c03355" />




---

## קבצים במאגר

* `main.py` – קובץ ראשי להרצת המערכת
* `operations/` –עבור שולחן databse קבצי גישה ל
* `database.py` – התחברות למסד נתונים
* `screens/` – קבצי GUI מופרדים
* `instructions/` – הוראות הרצה
* `README.md` – דוח זה

---


