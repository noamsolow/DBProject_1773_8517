# advanced_functions.py
from app.database import db_manager
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


class AdvancedFunctions:
    def __init__(self):
        pass

    def get_workers_with_most_hours(self):
        """Query workers with most working hours"""
        try:
            query = """
                SELECT p.firstname || ' ' || p.lastname as worker_name,
                       w.job,
                       COUNT(s.pid) as total_shifts,
                       SUM(EXTRACT(EPOCH FROM (s.clock_out - s.clock_in)) / 3600) as total_hours
                FROM person p
                JOIN worker w ON p.pid = w.pid
                LEFT JOIN shift s ON p.pid = s.pid
                GROUP BY p.pid, p.firstname, p.lastname, w.job
                HAVING SUM(EXTRACT(EPOCH FROM (s.clock_out - s.clock_in)) / 3600) > 0
                ORDER BY total_hours DESC
                LIMIT 10
            """
            return db_manager.execute_query(query, fetch='all')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute query: {str(e)}")
            return []

    def get_equipment_maintenance_needs(self):
        """Query equipment that needs maintenance"""
        try:
            query = """
                SELECT e.name, e.category, e.brand, e.warranty_expiry,
                       CASE 
                           WHEN e.warranty_expiry < CURRENT_DATE THEN 'Expired'
                           WHEN e.warranty_expiry < CURRENT_DATE + INTERVAL '30 days' THEN 'Expiring Soon'
                           ELSE 'Valid'
                       END as warranty_status,
                       COUNT(m.contract_id) as maintenance_count
                FROM equipment e
                LEFT JOIN maintenance m ON e.equipment_id = m.equipment_id
                GROUP BY e.equipment_id, e.name, e.category, e.brand, e.warranty_expiry
                ORDER BY e.warranty_expiry ASC
            """
            return db_manager.execute_query(query, fetch='all')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute query: {str(e)}")
            return []

    def get_worker_shift_summary(self, worker_id):
        """Execute worker shift summary function"""
        try:
            query = "SELECT * FROM get_worker_shift_summary(%s)"
            result = db_manager.execute_query(query, (worker_id,), fetch='one')
            return result
        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute function: {str(e)}")
            return None

    def get_equipment_maintenance_status(self):
        """Execute equipment maintenance status function"""
        try:
            # Execute the function that returns a cursor
            cursor_query = "SELECT get_equipment_maintenance_status()"
            cursor_name = db_manager.execute_query(cursor_query, fetch='one')[0]

            # Fetch all results from the cursor
            fetch_query = f'FETCH ALL IN "{cursor_name}"'
            results = db_manager.execute_query(fetch_query, fetch='all')
            return results
        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute function: {str(e)}")
            return []

    def update_worker_contract(self, worker_id, job_title, contract_type, wage_increase):
        """Execute update worker contract procedure"""
        try:
            query = "CALL update_worker_contract(%s, %s, %s, %s)"
            db_manager.execute_query(query, (worker_id, job_title, contract_type, wage_increase))
            db_manager.commit()
            return True
        except Exception as e:
            db_manager.rollback()
            messagebox.showerror("Error", f"Failed to execute procedure: {str(e)}")
            return False

    def process_equipment_orders(self, supplier_id, order_date):
        """Execute process equipment orders procedure"""
        try:
            query = "CALL process_equipment_orders(%s, %s)"
            db_manager.execute_query(query, (supplier_id, order_date))
            db_manager.commit()
            return True
        except Exception as e:
            db_manager.rollback()
            messagebox.showerror("Error", f"Failed to execute procedure: {str(e)}")
            return False

    def get_workers_for_contract_update(self):
        """Get list of workers for contract updates"""
        try:
            query = """
                SELECT p.pid, p.firstname || ' ' || p.lastname as full_name, w.job, w.contract
                FROM person p
                JOIN worker w ON p.pid = w.pid
                ORDER BY p.firstname
            """
            return db_manager.execute_query(query, fetch='all')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get workers: {str(e)}")
            return []


class ContractUpdateDialog:
    def __init__(self, parent):
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Update Worker Contract")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()

        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Worker selection
        tk.Label(main_frame, text="Worker:", font=("Arial", 10)).grid(
            row=0, column=0, sticky="e", padx=5, pady=10)
        self.worker_combo = ttk.Combobox(main_frame, width=22, state="readonly")
        self.worker_combo.grid(row=0, column=1, padx=5, pady=10)
        self.load_workers()

        # Job title
        tk.Label(main_frame, text="New Job Title:", font=("Arial", 10)).grid(
            row=1, column=0, sticky="e", padx=5, pady=10)
        self.job_entry = tk.Entry(main_frame, font=("Arial", 10), width=25)
        self.job_entry.grid(row=1, column=1, padx=5, pady=10)

        # Contract type
        tk.Label(main_frame, text="Contract Type:", font=("Arial", 10)).grid(
            row=2, column=0, sticky="e", padx=5, pady=10)
        self.contract_entry = tk.Entry(main_frame, font=("Arial", 10), width=25)
        self.contract_entry.grid(row=2, column=1, padx=5, pady=10)

        # Wage increase
        tk.Label(main_frame, text="Wage Increase ($):", font=("Arial", 10)).grid(
            row=3, column=0, sticky="e", padx=5, pady=10)
        self.wage_entry = tk.Entry(main_frame, font=("Arial", 10), width=25)
        self.wage_entry.grid(row=3, column=1, padx=5, pady=10)
        self.wage_entry.insert(0, "0")

        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        tk.Button(button_frame, text="Update", command=self.save,
                  bg="#27ae60", fg="white", width=10).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=self.cancel,
                  bg="#e74c3c", fg="white", width=10).pack(side="right", padx=5)

    def load_workers(self):
        """Load workers into combobox"""
        try:
            adv_func = AdvancedFunctions()
            self.workers = adv_func.get_workers_for_contract_update()

            worker_names = [f"{worker[1]} (ID: {worker[0]}) - {worker[2]}" for worker in self.workers]
            self.worker_combo['values'] = worker_names
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load workers: {str(e)}")

    def save(self):
        try:
            if self.worker_combo.current() == -1:
                messagebox.showerror("Error", "Please select a worker")
                return

            self.result = {
                'worker_id': self.workers[self.worker_combo.current()][0],
                'job_title': self.job_entry.get().strip(),
                'contract_type': self.contract_entry.get().strip(),
                'wage_increase': float(self.wage_entry.get().strip() or 0)
            }

            if not self.result['job_title'] or not self.result['contract_type']:
                messagebox.showerror("Error", "Please fill job title and contract type")
                return

            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Wage increase must be a number")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving data: {str(e)}")

    def cancel(self):
        self.dialog.destroy()