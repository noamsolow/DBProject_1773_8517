# real_equipment_operations.py - Equipment Management for actual database schema
from app.database import db_manager
import tkinter as tk
from tkinter import ttk, messagebox


class EquipmentOperations:
    def __init__(self):
        pass

    def get_all_equipment(self):
        """Retrieve all equipment from existing equipment table"""
        try:
            query = """
                SELECT equipment_id, name, category, purchase_date, warranty_expiry, brand
                FROM equipment
                ORDER BY equipment_id
            """
            return db_manager.execute_query(query, fetch='all')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve equipment: {str(e)}")
            return []

    def add_equipment(self, equipment_data):
        """Add new equipment to database"""
        try:
            query = """
                INSERT INTO equipment (name, category, purchase_date, warranty_expiry, brand)
                VALUES (%(name)s, %(category)s, %(purchase_date)s, %(warranty_expiry)s, %(brand)s)
            """
            db_manager.execute_query(query, equipment_data)
            db_manager.commit()
            return True

        except Exception as e:
            db_manager.rollback()
            messagebox.showerror("Error", f"Failed to add equipment: {str(e)}")
            return False

    def update_equipment(self, equipment_id, equipment_data):
        """Update existing equipment"""
        try:
            query = """
                UPDATE equipment 
                SET name=%(name)s, category=%(category)s, purchase_date=%(purchase_date)s, 
                    warranty_expiry=%(warranty_expiry)s, brand=%(brand)s
                WHERE equipment_id=%(equipment_id)s
            """
            equipment_data['equipment_id'] = equipment_id
            db_manager.execute_query(query, equipment_data)
            db_manager.commit()
            return True

        except Exception as e:
            db_manager.rollback()
            messagebox.showerror("Error", f"Failed to update equipment: {str(e)}")
            return False

    def delete_equipment(self, equipment_id):
        """Delete equipment from database"""
        try:
            # First delete related equipment_supplier records
            delete_relations_query = "DELETE FROM equipment_supplier WHERE equipment_id = %s"
            db_manager.execute_query(delete_relations_query, (equipment_id,))

            # Then delete the equipment
            delete_equipment_query = "DELETE FROM equipment WHERE equipment_id = %s"
            db_manager.execute_query(delete_equipment_query, (equipment_id,))

            db_manager.commit()
            return True

        except Exception as e:
            db_manager.rollback()
            messagebox.showerror("Error", f"Failed to delete equipment: {str(e)}")
            return False

    def get_equipment_details(self, equipment_id):
        """Get detailed equipment information"""
        try:
            query = """
                SELECT equipment_id, name, category, purchase_date, warranty_expiry, brand
                FROM equipment
                WHERE equipment_id = %s
            """
            return db_manager.execute_query(query, (equipment_id,), fetch='one')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get equipment details: {str(e)}")
            return None


class EquipmentDialog:
    def __init__(self, parent, title, equipment_data=None):
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x350")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()

        # Form fields based on actual equipment table structure
        fields = [
            ("Equipment Name:", "name"),
            ("Category:", "category"),
            ("Brand:", "brand"),
            ("Purchase Date (YYYY-MM-DD):", "purchase_date"),
            ("Warranty Expiry (YYYY-MM-DD):", "warranty_expiry")
        ]

        self.entries = {}

        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        for i, (label_text, field_name) in enumerate(fields):
            tk.Label(main_frame, text=label_text, font=("Arial", 10)).grid(
                row=i, column=0, sticky="e", padx=5, pady=10)

            if field_name == "category":
                # Based on your schema, category appears to be a varchar field
                # You might want to restrict this to specific values
                combo = ttk.Combobox(main_frame, values=["Strength", "Cardio", "Flexibility", "Other"],
                                     width=22)
                combo.grid(row=i, column=1, padx=5, pady=10)
                self.entries[field_name] = combo
            else:
                entry = tk.Entry(main_frame, font=("Arial", 10), width=25)
                entry.grid(row=i, column=1, padx=5, pady=10)
                self.entries[field_name] = entry

        # Fill data if editing
        if equipment_data:
            field_mapping = {
                'name': equipment_data[1] if len(equipment_data) > 1 else '',
                'category': equipment_data[2] if len(equipment_data) > 2 else '',
                'purchase_date': str(equipment_data[3]) if len(equipment_data) > 3 and equipment_data[3] else '',
                'warranty_expiry': str(equipment_data[4]) if len(equipment_data) > 4 and equipment_data[4] else '',
                'brand': equipment_data[5] if len(equipment_data) > 5 else ''
            }

            for field_name, value in field_mapping.items():
                if field_name in self.entries and value:
                    if field_name == "category":
                        self.entries[field_name].set(str(value))
                    else:
                        self.entries[field_name].insert(0, str(value))

        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)

        tk.Button(button_frame, text="Save", command=self.save,
                  bg="#27ae60", fg="white", width=10).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=self.cancel,
                  bg="#e74c3c", fg="white", width=10).pack(side="right", padx=5)

    def save(self):
        try:
            self.result = {}
            required_fields = ['name', 'category']

            for field_name, entry in self.entries.items():
                if field_name == "category":
                    value = entry.get()
                else:
                    value = entry.get().strip()

                if not value and field_name in required_fields:
                    messagebox.showerror("Error", f"Field '{field_name}' is required")
                    return

                self.result[field_name] = value if value else None

            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error saving data: {str(e)}")

    def cancel(self):
        self.dialog.destroy()