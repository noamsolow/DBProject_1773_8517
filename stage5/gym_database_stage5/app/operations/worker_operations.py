from app.database import db_manager
import tkinter as tk
from tkinter import ttk, messagebox


class WorkerOperations:
    def __init__(self):
        pass


    def get_all_workers(self):
        """Retrieve all workers from existing worker table"""
        try:
            query = """
                SELECT w.pid, p.firstname, p.lastname, w.job, w.contract, w.dateofeployment
                FROM worker w
                JOIN person p ON w.pid = p.pid
                ORDER BY w.pid
            """
            return db_manager.execute_query(query, fetch='all')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve workers: {str(e)}")
            return []

    def add_worker(self, worker_data):
        """Add new worker to database"""
        try:
            # Check if person exists
            person_check_query = "SELECT pid FROM person WHERE pid = %(pid)s"
            existing_person = db_manager.execute_query(person_check_query, {'pid': worker_data['pid']}, fetch='one')

            if not existing_person:
                person_query = """
                    INSERT INTO person (pid, firstname, lastname, dateofb, address, phone, email)
                    VALUES (%(pid)s, %(firstname)s, %(lastname)s, %(dateofb)s, %(address)s, %(phone)s, %(email)s)
                """
                db_manager.execute_query(person_query, worker_data)

            # Insert into worker
            worker_query = """
                INSERT INTO worker (pid, job, contract, dateofeployment)
                VALUES (%(pid)s, %(job)s, %(contract)s, %(dateofeployment)s)
            """
            db_manager.execute_query(worker_query, worker_data)

            db_manager.commit()
            return True
        except Exception as e:
            db_manager.rollback()
            messagebox.showerror("Error", f"Failed to add worker: {str(e)}")
            return False

    def update_worker(self, worker_pid, worker_data):
        """Update existing worker"""
        try:
            worker_data['pid'] = worker_pid

            person_query = """
                UPDATE person 
                SET firstname = %(firstname)s,
                    lastname = %(lastname)s,
                    dateofb = %(dateofb)s,
                    address = %(address)s,
                    phone = %(phone)s,
                    email = %(email)s
                WHERE pid = %(pid)s
            """
            db_manager.execute_query(person_query, worker_data)

            worker_query = """
                UPDATE worker 
                SET job = %(job)s,
                    contract = %(contract)s,
                    dateofeployment = %(dateofeployment)s
                WHERE pid = %(pid)s
            """
            db_manager.execute_query(worker_query, worker_data)

            db_manager.commit()
            return True
        except Exception as e:
            db_manager.rollback()
            messagebox.showerror("Error", f"Failed to update worker: {str(e)}")
            return False

    def delete_worker(self, worker_pid):
        """Delete worker from database"""
        try:
            # Delete from related equipment_supplier (if any)
            db_manager.execute_query("DELETE FROM equipment_supplier WHERE pid = %s", (worker_pid,))
            db_manager.execute_query("DELETE FROM worker WHERE pid = %s", (worker_pid,))
            # Optionally: delete from person too
            # db_manager.execute_query("DELETE FROM person WHERE pid = %s", (worker_pid,))
            db_manager.commit()
            return True
        except Exception as e:
            db_manager.rollback()
            messagebox.showerror("Error", f"Failed to delete worker: {str(e)}")
            return False

    def get_worker_details(self, worker_pid):
        """Get detailed worker information"""
        try:
            query = """
                SELECT w.pid, p.firstname, p.lastname, p.dateofb, p.address, p.phone, p.email,
                       w.job, w.contract, w.dateofeployment
                FROM worker w
                JOIN person p ON w.pid = p.pid
                WHERE w.pid = %s
            """
            return db_manager.execute_query(query, (worker_pid,), fetch='one')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get worker details: {str(e)}")
            return None

    def get_next_pid(self):
        """Get next available PID"""
        try:
            result = db_manager.execute_query("SELECT COALESCE(MAX(pid), 0) + 1 FROM person", fetch='one')
            return result[0] if result else 1
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get next PID: {str(e)}")
            return 1

class WorkerDialog:
    def __init__(self, parent, title, worker_data=None):
        self.result = None
        self.worker_ops = WorkerOperations()

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("450x600")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()

        self.dialog.transient(parent)

        # Define fields (same names used in DB and data dict)
        fields = [
            ("PID:", "pid"),
            ("First Name:", "firstname"),
            ("Last Name:", "lastname"),
            ("Date of Birth (YYYY-MM-DD):", "dateofb"),
            ("Address:", "address"),
            ("Phone:", "phone"),
            ("Email:", "email"),
            ("Job:", "job"),
            ("Contract:", "contract"),
            ("Date of Deployment (YYYY-MM-DD):", "dateofeployment")
        ]

        self.entries = {}

        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Create form fields
        for i, (label, field_name) in enumerate(fields):
            tk.Label(main_frame, text=label, font=("Arial", 10)).grid(row=i, column=0, sticky="e", pady=5)
            entry = tk.Entry(main_frame, font=("Arial", 10), width=30)

            # If creating new worker, auto-fill PID
            if field_name == "pid" and not worker_data:
                pid = self.worker_ops.get_next_pid()
                entry.insert(0, str(pid))
                entry.config(state="readonly")

            entry.grid(row=i, column=1, pady=5)
            self.entries[field_name] = entry

        # Fill data if editing
        if worker_data:
            keys = list(self.entries.keys())
            for i, value in enumerate(worker_data):
                if i < len(keys):
                    self.entries[keys[i]].insert(0, str(value))

        # Buttons
        btn_frame = tk.Frame(main_frame)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=15)

        tk.Button(btn_frame, text="Save", command=self.save, bg="#2ecc71", fg="white", width=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.dialog.destroy, bg="#e74c3c", fg="white", width=10).pack(side="right", padx=5)

    def save(self):
        self.result = {}
        required = ["pid", "firstname", "lastname", "job"]

        for field_name, entry in self.entries.items():
            val = entry.get().strip()
            if not val and field_name in required:
                messagebox.showerror("Error", f"Field '{field_name}' is required")
                return

            if field_name == "pid":
                try:
                    val = int(val)
                except ValueError:
                    messagebox.showerror("Error", "PID must be a number")
                    return

            if field_name == "phone" and val:
                try:
                    float(val)
                except ValueError:
                    messagebox.showerror("Error", "Phone must be numeric")
                    return

            self.result[field_name] = val if val else None

        self.dialog.destroy()
