from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from typing import List

app = FastAPI()

# CORS - allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Database Configuration ===
DB_CONFIG = {
    "dbname": "intagratedDBs",
    "user": "nsolow",
    "password": "noam2004",
    "host": "localhost",
    "port": "5432"
}


# === Pydantic Models ===
class Equipment(BaseModel):
    name: str
    category: str
    purchase_date: str
    warranty_expiry: str
    brand: str

from typing import Optional

class EquipmentOut(Equipment):
    id: int
    brand: Optional[str]  # allow null brand


# === Helper ===
def get_conn():
    return psycopg2.connect(**DB_CONFIG)

# === API Endpoints ===

@app.get("/equipment", response_model=List[EquipmentOut])
def get_equipment():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM equipment")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        EquipmentOut(
            id=row[0],
            name=row[1],
            category=row[2],
            purchase_date=str(row[3]),
            warranty_expiry=str(row[4]),
            brand=row[5]
        ) for row in rows
    ]

@app.post("/equipment", response_model=EquipmentOut)
def create_equipment(equipment: Equipment):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO equipment (name, category, purchase_date, warranty_expiry, brand)
        VALUES (%s, %s, %s, %s, %s) RETURNING equipment_id
    """, (equipment.name, equipment.category, equipment.purchase_date, equipment.warranty_expiry, equipment.brand))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return EquipmentOut(id=new_id, **equipment.dict())

@app.delete("/equipment/{equipment_id}")
def delete_equipment(equipment_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM equipment WHERE equipment_id = %s", (equipment_id,))
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Equipment not found")
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Deleted successfully"}

# Additional endpoints like /workers, /suppliers, and function/procedure triggers can be added next.
