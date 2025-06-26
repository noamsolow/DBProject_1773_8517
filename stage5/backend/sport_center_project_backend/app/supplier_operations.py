# real_supplier_operations.py - Supplier Management for actual database schema
from app.database import db_manager
import tkinter as tk
from tkinter import ttk, messagebox


class SupplierOperations:
    def __init__(self):
        pass

    def get_all_suppliers(self):
        """Retrieve all suppliers from existing supplier table"""
        try:
            query = """
SELECT s.pid, p.firstname, p.lastname, p.dateofb, 
                       p.address, p.phone, p.email
                FROM supplier s
                JOIN person p ON s.pid = p.pid
                ORDER BY s.pid
            """
            return db_manager.execute_query(query, fetch='all')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve suppliers: {str(e)}")
            return []

    def add_supplier(self, supplier_data):
        """Add new supplier to database"""
        try:
            # First, check if person exists, if not create them
            person_check_query = "SELECT pid FROM person WHERE pid = %(pid)s"
            existing_person = db_manager.execute_query(person_check_query, {'pid': supplier_data['pid']}, fetch='one')

            if not existing_person:
                # Insert into person table first
                person_query = """
                    INSERT INTO person (pid, firstname, lastname, dateofb, address, phone, email)
                    VALUES (%(pid)s, %(firstname)s, %(lastname)s, %(dateofb)s, %(address)s, %(phone)s, %(email)s)
                """
                db_manager.execute_query(person_query, supplier_data)

            # Insert into supplier table
            supplier_query = """
                INSERT INTO supplier (pid)
                VALUES (%(pid)s)
            """
            db_manager.execute_query(supplier_query, supplier_data)

            db_manager.commit()
            return True

        except Exception as e:
            db_manager.rollback()
            messagebox.showerror("Error", f"Failed to add supplier: {str(e)}")
            return False

    def update_supplier(self, supplier_id, supplier_data):
        """Update existing supplier"""
        try:
            # Get the PID for this supplier
            pid_query = "SELECT pid FROM supplier WHERE pid = %s"
            pid_result = db_manager.execute_query(pid_query, (supplier_id,), fetch='one')

            if not pid_result:
                messagebox.showerror("Error", "Supplier not found")
                return False

            pid = pid_result[0]

            # Update person table
            person_query = """
                UPDATE person 
                SET firstname=%(firstname)s, lastname=%(lastname)s, dateofb=%(dateofb)s,
                    address=%(address)s, phone=%(phone)s, email=%(email)s
                WHERE pid=%(pid)s
            """
            supplier_data['pid'] = pid  # Ensure 'pid' is in the dict

            db_manager.execute_query(person_query, supplier_data)

            db_manager.commit()
            return True

        except Exception as e:
            db_manager.rollback()
            messagebox.showerror("Error", f"Failed to update supplier: {str(e)}")
            return False

    def delete_supplier(self, supplier_id):
        """Delete supplier from database"""
        try:
            # Get the PID for this supplier
            pid_query = "SELECT pid FROM supplier WHERE pid = %s"
            pid_result = db_manager.execute_query(pid_query, (supplier_id,), fetch='one')

            if not pid_result:
                messagebox.showerror("Error", "Supplier not found")
                return False

            pid = pid_result[0]

            # First delete related equipment_supplier records
            delete_relations_query = "DELETE FROM equipment_supplier WHERE pid = %s"
            db_manager.execute_query(delete_relations_query, (pid,))

            # Delete from supplier table
            delete_supplier_query = "DELETE FROM supplier WHERE pid = %s"
            db_manager.execute_query(delete_supplier_query, (supplier_id,))

            # Optionally delete from person table (be careful with this)
            # delete_person_query = "DELETE FROM person WHERE pid = %s"
            # db_manager.execute_query(delete_person_query, (pid,))

            db_manager.commit()
            return True

        except Exception as e:
            db_manager.rollback()
            messagebox.showerror("Error", f"Failed to delete supplier: {str(e)}")
            return False

    def get_supplier_details(self, supplier_id):
        """Get detailed supplier information"""
        try:
            query = """
                SELECT s.pid, s.pid, p.firstname, p.lastname, p.dateofb, 
                       p.address, p.phone, p.email
                FROM supplier s
                JOIN person p ON s.pid = p.pid
                WHERE s.pid = %s
            """
            return db_manager.execute_query(query, (supplier_id,), fetch='one')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get supplier details: {str(e)}")
            return None

    def get_next_pid(self):
        """Get next available PID"""
        try:
            query = "SELECT COALESCE(MAX(pid), 0) + 1 FROM person"
            result = db_manager.execute_query(query, fetch='one')
            return result[0] if result else 1
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get next PID: {str(e)}")
            return 1


class SupplierDialog:
    def __init__(self, parent, title, supplier_data=None):
        self.result = None
        self.supplier_ops = SupplierOperations()

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("450x450")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.transient(parent)

        # Form fields based on actual schema (person table fields)
        fields = [
            ("PID:", "pid"),
            ("First Name:", "firstname"),
            ("Last Name:", "lastname"),
            ("Date of Birth (YYYY-MM-DD):", "dateofb"),
            ("Address:", "address"),
            ("Phone:", "phone"),
            ("Email:", "email")
        ]

        self.entries = {}

        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Create form fields
        for i, (label_text, field_name) in enumerate(fields):
            tk.Label(main_frame, text=label_text, font=("Arial", 10)).grid(
                row=i, column=0, sticky="e", padx=5, pady=10)

            if field_name == "pid":
                entry = tk.Entry(main_frame, font=("Arial", 10), width=30)
                if not supplier_data:  # New supplier - auto-generate PID
                    next_pid = self.supplier_ops.get_next_pid()
                    entry.insert(0, str(next_pid))
                    entry.config(state="readonly")
            else:
                entry = tk.Entry(main_frame, font=("Arial", 10), width=30)

            entry.grid(row=i, column=1, padx=5, pady=10)
            self.entries[field_name] = entry

        # Fill data if editing
        if supplier_data:
            field_mapping = {
                'pid': supplier_data[1] if len(supplier_data) > 1 else '',
                'firstname': supplier_data[2] if len(supplier_data) > 2 else '',
                'lastname': supplier_data[3] if len(supplier_data) > 3 else '',
                'dateofb': str(supplier_data[4]) if len(supplier_data) > 4 and supplier_data[4] else '',
                'address': supplier_data[5] if len(supplier_data) > 5 else '',
                'phone': str(supplier_data[6]) if len(supplier_data) > 6 and supplier_data[6] else '',
                'email': supplier_data[7] if len(supplier_data) > 7 else ''
            }

            for field_name, value in field_mapping.items():
                if field_name in self.entries and value:
                    self.entries[field_name].delete(0, tk.END)
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
            required_fields = ['pid', 'firstname', 'lastname']

            for field_name, entry in self.entries.items():
                value = entry.get().strip()
                if not value and field_name in required_fields:
                    messagebox.showerror("Error", f"Field '{field_name}' is required")
                    return

                # Convert PID to integer
                if field_name == 'pid' and value:
                    try:
                        value = int(value)
                    except ValueError:
                        messagebox.showerror("Error", "PID must be a number")
                        return

                # Convert phone to numeric if provided
                if field_name == 'phone' and value:
                    try:
                        value = float(value)
                    except ValueError:
                        messagebox.showerror("Error", "Phone must be numeric")
                        return

                self.result[field_name] = value if value else None

            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error saving data: {str(e)}")

    def cancel(self):
        self.dialog.destroy()