# real_equipment_supplier_operations.py - Equipment-Supplier Relationship Management for actual schema
from app.database import db_manager
import tkinter as tk
from tkinter import ttk, messagebox


class EquipmentSupplierOperations:
    def __init__(self):
        pass

    def get_all_equipment_suppliers(self):
        """Retrieve all equipment-supplier relationships with details"""
        try:
            query = """
                 SELECT 
                    es.equipment_id,
                    e.name as equipment_name,
                    e.category,
                    es.pid,
                    p.firstname || ' ' || p.lastname as person_name,
                    es.quantity,
                    es.supply_date

                FROM equipment_supplier es
                JOIN equipment e ON es.equipment_id = e.equipment_id
                JOIN person p ON es.pid = p.pid
                LEFT JOIN worker w ON es.pid = w.pid
                LEFT JOIN supplier s ON es.pid = s.pid
                ORDER BY es.supply_date DESC
            """
            return db_manager.execute_query(query, fetch='all')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve equipment-supplier data: {str(e)}")
            return []

    def add_equipment_supplier(self, es_data):
        """Add new equipment-supplier relationship"""
        try:
            query = """
                INSERT INTO equipment_supplier (equipment_id, pid, quantity, supply_date)
                VALUES (%(equipment_id)s, %(pid)s, %(quantity)s, %(supply_date)s)
            """
            db_manager.execute_query(query, es_data)
            db_manager.commit()
            return True

        except Exception as e:
            db_manager.rollback()
            messagebox.showerror("Error", f"Failed to add equipment-supplier relationship: {str(e)}")
            return False

    def update_equipment_supplier(self, original_data, es_data):
        """Update existing equipment-supplier relationship"""
        try:
            query = """
                UPDATE equipment_supplier 
                SET pid=%(pid)s, quantity=%(quantity)s, supply_date=%(supply_date)s
                WHERE equipment_id=%(equipment_id)s AND pid=%(original_pid)s
            """
            es_data['equipment_id'] = original_data[0]
            es_data['original_pid'] = original_data[3]
            db_manager.execute_query(query, es_data)
            db_manager.commit()
            return True

        except Exception as e:
            db_manager.rollback()
            messagebox.showerror("Error", f"Failed to update equipment-supplier relationship: {str(e)}")
            return False

    def delete_equipment_supplier(self, equipment_id, pid):
        """Delete equipment-supplier relationship"""
        try:
            query = "DELETE FROM equipment_supplier WHERE equipment_id = %s AND pid = %s"
            db_manager.execute_query(query, (equipment_id, pid))
            db_manager.commit()
            return True

        except Exception as e:
            db_manager.rollback()
            messagebox.showerror("Error", f"Failed to delete equipment-supplier relationship: {str(e)}")
            return False

    def get_equipment_list(self):
        """Get list of available equipment"""
        try:
            query = "SELECT equipment_id, name, category FROM equipment ORDER BY name"
            return db_manager.execute_query(query, fetch='all')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get equipment list: {str(e)}")
            return []

    def get_person_list(self):
        """Get list of suppliers only"""
        try:
            query = """
                SELECT p.pid, p.firstname, p.lastname
                FROM person p
                JOIN supplier s ON p.pid = s.pid
                ORDER BY p.firstname
            """
            return db_manager.execute_query(query, fetch='all')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get supplier list: {str(e)}")
            return []


class EquipmentSupplierDialog:
    def __init__(self, parent, title, es_data=None):
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x350")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.transient(parent)

        self.es_ops = EquipmentSupplierOperations()

        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Equipment selection
        tk.Label(main_frame, text="Equipment:", font=("Arial", 10)).grid(
            row=0, column=0, sticky="e", padx=5, pady=15)
        self.equipment_combo = ttk.Combobox(main_frame, width=35, state="readonly")
        self.equipment_combo.grid(row=0, column=1, padx=5, pady=15)
        self.load_equipment()

        # Person selection (worker or supplier)
        tk.Label(main_frame, text="Person (Worker/Supplier):", font=("Arial", 10)).grid(
            row=1, column=0, sticky="e", padx=5, pady=15)
        self.person_combo = ttk.Combobox(main_frame, width=35, state="readonly")
        self.person_combo.grid(row=1, column=1, padx=5, pady=15)
        self.load_persons()

        # Quantity
        tk.Label(main_frame, text="Quantity:", font=("Arial", 10)).grid(
            row=2, column=0, sticky="e", padx=5, pady=15)
        self.quantity_entry = tk.Entry(main_frame, font=("Arial", 10), width=37)
        self.quantity_entry.grid(row=2, column=1, padx=5, pady=15)

        # Supply date
        tk.Label(main_frame, text="Supply Date (YYYY-MM-DD):", font=("Arial", 10)).grid(
            row=3, column=0, sticky="e", padx=5, pady=15)
        self.supply_date_entry = tk.Entry(main_frame, font=("Arial", 10), width=37)
        self.supply_date_entry.grid(row=3, column=1, padx=5, pady=15)

        # Fill data if editing
        if es_data:
            self.fill_edit_data(es_data)

        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=25)

        tk.Button(button_frame, text="Save", command=self.save,
                  bg="#27ae60", fg="white", width=12).pack(side="left", padx=10)
        tk.Button(button_frame, text="Cancel", command=self.cancel,
                  bg="#e74c3c", fg="white", width=12).pack(side="right", padx=10)

    def load_equipment(self):
        """Load equipment into combobox"""
        try:
            self.equipment_list = self.es_ops.get_equipment_list()
            equipment_options = [f"{eq[1]} ({eq[2]}) - ID: {eq[0]}" for eq in self.equipment_list]
            self.equipment_combo['values'] = equipment_options
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load equipment: {str(e)}")

    def load_persons(self):
        """Load suppliers into combobox"""
        try:
            self.person_list = self.es_ops.get_person_list()
            person_options = [f"{person[1]} {person[2]} - ID: {person[0]}" for person in self.person_list]
            self.person_combo['values'] = person_options
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load suppliers: {str(e)}")

    def fill_edit_data(self, es_data):
        """Fill form with existing data for editing"""
        try:
            # Find and select equipment
            for i, eq in enumerate(self.equipment_list):
                if eq[0] == es_data[0]:  # equipment_id
                    self.equipment_combo.current(i)
                    break

            # Find and select person
            for i, person in enumerate(self.person_list):
                if person[0] == es_data[3]:  # pid
                    self.person_combo.current(i)
                    break

            # Fill other fields
            self.quantity_entry.insert(0, str(es_data[5]) if es_data[5] else '')
            self.supply_date_entry.insert(0, str(es_data[6]) if es_data[6] else '')

        except Exception as e:
            messagebox.showerror("Error", f"Error filling form data: {str(e)}")

    def save(self):
        try:
            # Validate selections
            if self.equipment_combo.current() == -1:
                messagebox.showerror("Error", "Please select equipment")
                return

            if self.person_combo.current() == -1:
                messagebox.showerror("Error", "Please select a person")
                return

            # Get selected IDs
            equipment_id = self.equipment_list[self.equipment_combo.current()][0]
            pid = self.person_list[self.person_combo.current()][0]

            # Get other values
            quantity = self.quantity_entry.get().strip()
            supply_date = self.supply_date_entry.get().strip()

            # Validate required fields
            if not supply_date:
                messagebox.showerror("Error", "Supply date is required")
                return

            # Convert quantity to integer
            try:
                quantity = int(quantity) if quantity else None
            except ValueError:
                messagebox.showerror("Error", "Quantity must be an integer")
                return

            self.result = {
                'equipment_id': equipment_id,
                'pid': pid,
                'quantity': quantity,
                'supply_date': supply_date
            }

            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error saving data: {str(e)}")

    def cancel(self):
        self.dialog.destroy()