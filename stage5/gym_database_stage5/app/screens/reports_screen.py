# screens/reports_screen.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from app.database import db_manager


class ReportsScreen:
    def __init__(self, app):
        self.app = app
        self.root = app.root
        self.content_frame = app.content_frame
        self.update_status = app.update_status
        self.results_text = None

    def show_reports_screen(self):
        """Show reports and analytics screen"""
        self.app.clear_content()
        self.content_frame.configure(bg="#d6c1e3")

        # Wrapper Frame to control layout
        wrapper = tk.Frame(self.content_frame, bg="#d798eb")
        wrapper.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header = tk.Frame(wrapper, bg="#ffe8fb")
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="📊 Reports & Analytics",font=("Arial", 18, "bold"), fg="#4c2861", bg="#ffe8fb").pack(side="left")

        # Standard Reports Section - Made more compact
        std_frame = tk.LabelFrame(wrapper, text="Standard Reports",
                                  font=("Arial", 12, "bold"), fg="#4c2861", bg="#ffe8fb",
                                  padx=10, pady=8, bd=1)
        std_frame.pack(fill="x", pady=(0, 8))
        std_frame.pack_propagate(False)
        std_frame.configure(height=90)  # Increased height for bigger buttons

        standard_buttons = [
            ("📌 Equipment by Person", self.report_equipment_by_person, "#871791"),
            ("📋 Person Summary", self.report_person_summary, "#871791"),
            ("📈 Equipment Stats", self.report_equipment_stats, "#871791"),
            ("📆 Supply Timeline", self.report_supply_timeline, "#871791")
        ]
        self._render_buttons(std_frame, standard_buttons)

        # Advanced Functions Section - Made more compact
        adv_frame = tk.LabelFrame(wrapper, text="Advanced Functions & Procedures",
                                  font=("Arial", 12, "bold"), fg="#4c2861", bg="#ffe8fb",
                                  padx=10, pady=8, bd=1)
        adv_frame.pack(fill="x", pady=(0, 15))
        adv_frame.pack_propagate(False)
        adv_frame.configure(height=90)  # Increased height for bigger buttons

        advanced_buttons = [
            ("🧑‍🏭 Worker Shift Summary", self.func_worker_shift_summary, "#e81cda"),
            ("🛠 Maintenance Status", self.func_equipment_maintenance_status, "#e81cda"),
            ("✍️ Update Worker Contract", self.proc_update_worker_contract, "#ff73e8"),
            ("📦 Process Orders", self.proc_process_equipment_orders, "#ff73e8")
        ]
        self._render_buttons(adv_frame, advanced_buttons)

        # Results Section - Expanded to take up much more space
        results_frame = tk.LabelFrame(wrapper, text="Report Results",
                                      font=("Arial", 12, "bold"), fg="#4c2861", bg="#ffe8fb",
                                      padx=15, pady=15)
        results_frame.pack(fill="both", expand=True)

        # Create a frame for the text widget and scrollbars
        text_frame = tk.Frame(results_frame, bg="#ffffff")
        text_frame.pack(fill="both", expand=True)

        self.results_text = tk.Text(
            text_frame,
            font=("Consolas", 9),  # Slightly larger font
            bg="#f8f9fa",
            fg="#21051d",
            wrap="none",
            relief="flat",
            bd=0,
            spacing3=8,  # Increased line spacing
            padx=20,  # More padding
            pady=15
        )

        v_scroll = ttk.Scrollbar(text_frame, orient="vertical", command=self.results_text.yview)
        h_scroll = ttk.Scrollbar(text_frame, orient="horizontal", command=self.results_text.xview)

        self.results_text.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Grid layout for better control
        self.results_text.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        # Configure grid weights to make text widget expand
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        # Add a placeholder text to show the expanded area
        self.results_text.insert(tk.END, "Report results will appear here...\n")
        self.results_text.insert(tk.END, "Click any report button above to generate a report.\n\n")
        self.results_text.insert(tk.END, "✓ Expanded results area for better visibility\n")
        self.results_text.insert(tk.END, "✓ Improved scrolling and layout\n")
        self.results_text.insert(tk.END, "✓ Larger font and better spacing\n")

        self.update_status("Reports screen loaded")

    def _render_buttons(self, parent, buttons):
        """Render buttons in a 2-column layout with more compact styling"""
        for i, (text, command, color) in enumerate(buttons):
            btn = tk.Button(parent, text=text, command=command,
                            font=("Arial", 10, "bold"), bg=color, fg="white",
                            width=28, height=1, cursor="hand2", relief="flat")  # Reduced height
            btn.grid(row=i // 2, column=i % 2, padx=15, pady=8, sticky="ew")  # Reduced padding
            parent.grid_columnconfigure(i % 2, weight=1)

    def report_equipment_by_person(self):
        """Generate equipment by person report"""
        try:
            query = """
                SELECT 
                    p.firstname || ' ' || p.lastname as person_name,
                    CASE 
                        WHEN w.pid IS NOT NULL THEN 'Worker'
                        WHEN s.pid IS NOT NULL THEN 'Supplier'
                        ELSE 'Person'
                    END as person_type,
                    COUNT(DISTINCT e.equipment_id) as equipment_count,
                    STRING_AGG(DISTINCT e.name, ', ') as equipment_list,
                    SUM(es.quantity) as total_quantity
                FROM person p
                LEFT JOIN worker w ON p.pid = w.pid
                LEFT JOIN supplier s ON p.pid = s.pid
                LEFT JOIN equipment_supplier es ON p.pid = es.pid
                LEFT JOIN equipment e ON es.equipment_id = e.equipment_id
                GROUP BY p.pid, p.firstname, p.lastname, w.pid, s.pid
                HAVING COUNT(DISTINCT e.equipment_id) > 0
                ORDER BY equipment_count DESC
            """
            results = db_manager.execute_query(query, fetch='all')

            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "EQUIPMENT BY PERSON REPORT\n")
            self.results_text.insert(tk.END, "=" * 80 + "\n")
            self.results_text.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for person_name, person_type, count, equipment_list, total_qty in results:
                self.results_text.insert(tk.END, f"Person: {person_name} ({person_type})\n")
                self.results_text.insert(tk.END, f"Equipment Count: {count}\n")
                self.results_text.insert(tk.END, f"Total Quantity: {total_qty or 0}\n")
                if equipment_list:
                    self.results_text.insert(tk.END, f"Equipment: {equipment_list}\n")
                self.results_text.insert(tk.END, "-" * 50 + "\n\n")

            self.update_status("Equipment by person report generated")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")

    def report_person_summary(self):
        """Generate person summary report"""
        try:
            query = """
                SELECT 
                    p.pid,
                    p.firstname || ' ' || p.lastname as full_name,
                    p.dateofb,
                    p.phone,
                    p.email,
                    CASE 
                        WHEN w.pid IS NOT NULL AND s.pid IS NOT NULL THEN 'Worker & Supplier'
                        WHEN w.pid IS NOT NULL THEN 'Worker'
                        WHEN s.pid IS NOT NULL THEN 'Supplier'
                        ELSE 'Person Only'
                    END as roles,
                    w.job,
                    w.contract,
                    COUNT(es.equipment_id) as equipment_relations
                FROM person p
                LEFT JOIN worker w ON p.pid = w.pid
                LEFT JOIN supplier s ON p.pid = s.pid
                LEFT JOIN equipment_supplier es ON p.pid = es.pid
                GROUP BY p.pid, p.firstname, p.lastname, p.dateofb, p.phone, p.email, 
                         w.pid, s.pid, w.job, w.contract
                ORDER BY p.pid
            """
            results = db_manager.execute_query(query, fetch='all')

            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "PERSON SUMMARY REPORT\n")
            self.results_text.insert(tk.END, "=" * 80 + "\n")
            self.results_text.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for pid, name, dob, phone, email, roles, job, contract, eq_count in results:
                self.results_text.insert(tk.END, f"ID: {pid} | {name}\n")
                self.results_text.insert(tk.END, f"Roles: {roles}\n")
                if job:
                    self.results_text.insert(tk.END, f"Job: {job}\n")
                if contract:
                    self.results_text.insert(tk.END, f"Contract: {contract}\n")
                self.results_text.insert(tk.END, f"Date of Birth: {dob or 'N/A'}\n")
                self.results_text.insert(tk.END, f"Phone: {phone or 'N/A'}\n")
                self.results_text.insert(tk.END, f"Email: {email or 'N/A'}\n")
                self.results_text.insert(tk.END, f"Equipment Relations: {eq_count}\n")
                self.results_text.insert(tk.END, "-" * 50 + "\n\n")

            self.update_status("Person summary report generated")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")

    def report_equipment_stats(self):
        """Generate equipment statistics report"""
        try:
            query = """
                SELECT 
                    e.category,
                    COUNT(*) as equipment_count,
                    COUNT(DISTINCT es.pid) as people_involved,
                    SUM(es.quantity) as total_quantity_supplied,
                    MIN(e.purchase_date) as oldest_purchase,
                    MAX(e.purchase_date) as newest_purchase,
                    COUNT(CASE WHEN e.warranty_expiry < CURRENT_DATE THEN 1 END) as expired_warranty,
                    STRING_AGG(DISTINCT e.brand, ', ') as brands
                FROM equipment e
                LEFT JOIN equipment_supplier es ON e.equipment_id = es.equipment_id
                GROUP BY e.category
                ORDER BY equipment_count DESC
            """
            results = db_manager.execute_query(query, fetch='all')

            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "EQUIPMENT STATISTICS REPORT\n")
            self.results_text.insert(tk.END, "=" * 80 + "\n")
            self.results_text.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for category, count, people, qty, oldest, newest, expired, brands in results:
                self.results_text.insert(tk.END, f"Category: {category}\n")
                self.results_text.insert(tk.END, f"Equipment Count: {count}\n")
                self.results_text.insert(tk.END, f"People Involved: {people or 0}\n")
                self.results_text.insert(tk.END, f"Total Quantity Supplied: {qty or 0}\n")
                self.results_text.insert(tk.END, f"Purchase Date Range: {oldest or 'N/A'} to {newest or 'N/A'}\n")
                self.results_text.insert(tk.END, f"Expired Warranties: {expired}\n")
                self.results_text.insert(tk.END, f"Brands: {brands or 'N/A'}\n")
                self.results_text.insert(tk.END, "-" * 50 + "\n\n")

            self.update_status("Equipment statistics report generated")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")

    def report_supply_timeline(self):
        """Generate supply timeline report"""
        try:
            query = """
                SELECT 
                    DATE_TRUNC('month', es.supply_date) as supply_month,
                    COUNT(*) as supply_count,
                    COUNT(DISTINCT es.equipment_id) as unique_equipment,
                    COUNT(DISTINCT es.pid) as unique_people,
                    SUM(es.quantity) as total_quantity,
                    STRING_AGG(DISTINCT e.category, ', ') as categories
                FROM equipment_supplier es
                JOIN equipment e ON es.equipment_id = e.equipment_id
                WHERE es.supply_date IS NOT NULL
                GROUP BY DATE_TRUNC('month', es.supply_date)
                ORDER BY supply_month DESC
                LIMIT 12
            """
            results = db_manager.execute_query(query, fetch='all')

            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "SUPPLY TIMELINE REPORT\n")
            self.results_text.insert(tk.END, "=" * 80 + "\n")
            self.results_text.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.results_text.insert(tk.END, "Last 12 months of supply activity\n\n")

            for month, count, eq_count, people, qty, categories in results:
                month_str = month.strftime('%Y-%m') if month else 'Unknown'
                self.results_text.insert(tk.END, f"Month: {month_str}\n")
                self.results_text.insert(tk.END, f"Supply Events: {count}\n")
                self.results_text.insert(tk.END, f"Unique Equipment: {eq_count}\n")
                self.results_text.insert(tk.END, f"People Involved: {people}\n")
                self.results_text.insert(tk.END, f"Total Quantity: {qty}\n")
                self.results_text.insert(tk.END, f"Categories: {categories}\n")
                self.results_text.insert(tk.END, "-" * 50 + "\n\n")

            self.update_status("Supply timeline report generated")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")

    def func_worker_shift_summary(self):
        """Execute worker shift summary function"""
        worker_id = simpledialog.askinteger("Worker Shift Summary",
                                            "Enter Worker ID:",
                                            minvalue=1)
        if not worker_id:
            return

        try:
            query = "SELECT * FROM get_worker_shift_summary(%s)"
            results = db_manager.execute_query(query, (worker_id,), fetch='all')

            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "WORKER SHIFT SUMMARY FUNCTION\n")
            self.results_text.insert(tk.END, "=" * 80 + "\n")
            self.results_text.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.results_text.insert(tk.END, f"Worker ID: {worker_id}\n\n")

            if results:
                for worker_name, total_shifts, total_hours, overtime_hours, total_pay in results:
                    self.results_text.insert(tk.END, f"Worker Name: {worker_name}\n")
                    self.results_text.insert(tk.END, f"Total Shifts: {total_shifts}\n")
                    self.results_text.insert(tk.END, f"Total Hours: {total_hours:.2f}\n")
                    self.results_text.insert(tk.END, f"Overtime Hours: {overtime_hours:.2f}\n")
                    self.results_text.insert(tk.END, f"Total Pay: ${total_pay:.2f}\n")
                    self.results_text.insert(tk.END, "-" * 50 + "\n")
            else:
                self.results_text.insert(tk.END, "Could not find worker.\n")

            self.update_status("Worker shift summary generated")

        except Exception:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Could not find worker.\n")
            self.update_status("Worker not found or error occurred")

    def func_equipment_maintenance_status(self):
        """Execute equipment maintenance status function (ref cursor)"""
        try:
            query = """
                SELECT 
                    e.equipment_id,
                    e.name,
                    e.category,
                    e.brand,
                    e.purchase_date,
                    e.warranty_expiry,
                    CASE 
                        WHEN e.warranty_expiry < CURRENT_DATE THEN 'EXPIRED'
                        WHEN e.warranty_expiry < CURRENT_DATE + INTERVAL '30 days' THEN 'EXPIRING_SOON'
                        ELSE 'VALID'
                    END as warranty_status,
                    COUNT(m.contract_id) as maintenance_count,
                    MAX(cj.service_date) as last_maintenance_date,
                    SUM(cj.cost) as total_maintenance_cost
                FROM equipment e
                LEFT JOIN maintenance m ON e.equipment_id = m.equipment_id
                LEFT JOIN contract_job cj ON m.contract_id = cj.contract_id
                GROUP BY e.equipment_id, e.name, e.category, e.brand, e.purchase_date, e.warranty_expiry
                ORDER BY e.equipment_id
            """
            results = db_manager.execute_query(query, fetch='all')

            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "EQUIPMENT MAINTENANCE STATUS FUNCTION\n")
            self.results_text.insert(tk.END, "=" * 80 + "\n")
            self.results_text.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            if results:
                for row in results:
                    eq_id, name, category, brand, purchase_date, warranty_expiry, warranty_status, maintenance_count, last_maintenance, total_cost = row
                    self.results_text.insert(tk.END, f"Equipment ID: {eq_id}\n")
                    self.results_text.insert(tk.END, f"Name: {name}\n")
                    self.results_text.insert(tk.END, f"Category: {category}\n")
                    self.results_text.insert(tk.END, f"Brand: {brand}\n")
                    self.results_text.insert(tk.END, f"Purchase Date: {purchase_date}\n")
                    self.results_text.insert(tk.END, f"Warranty Expiry: {warranty_expiry}\n")
                    self.results_text.insert(tk.END, f"Warranty Status: {warranty_status}\n")
                    self.results_text.insert(tk.END, f"Maintenance Count: {maintenance_count or 0}\n")
                    self.results_text.insert(tk.END, f"Last Maintenance: {last_maintenance or 'N/A'}\n")
                    self.results_text.insert(tk.END, f"Total Maintenance Cost: ${total_cost or 0:.2f}\n")
                    self.results_text.insert(tk.END, "-" * 50 + "\n\n")
            else:
                self.results_text.insert(tk.END, "No equipment data found.\n")

            self.update_status("Equipment maintenance status generated")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute function: {str(e)}")
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"ERROR: {str(e)}\n")

    def proc_update_worker_contract(self):
        """Execute update worker contract procedure"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Update Worker Contract")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))

        # Input fields
        tk.Label(dialog, text="Worker ID:", font=("Arial", 12)).pack(pady=5)
        worker_id_var = tk.StringVar()
        tk.Entry(dialog, textvariable=worker_id_var, font=("Arial", 11), width=20).pack(pady=5)

        tk.Label(dialog, text="New Job Title:", font=("Arial", 12)).pack(pady=5)
        job_title_var = tk.StringVar()
        tk.Entry(dialog, textvariable=job_title_var, font=("Arial", 11), width=20).pack(pady=5)

        tk.Label(dialog, text="New Contract Type:", font=("Arial", 12)).pack(pady=5)
        contract_var = tk.StringVar()
        contract_combo = ttk.Combobox(dialog, textvariable=contract_var,
                                      values=["Full-time", "Part-time", "Contract", "Temporary"])
        contract_combo.pack(pady=5)

        tk.Label(dialog, text="Wage Increase ($):", font=("Arial", 12)).pack(pady=5)
        wage_var = tk.StringVar(value="0")
        tk.Entry(dialog, textvariable=wage_var, font=("Arial", 11), width=20).pack(pady=5)

        def execute_procedure():
            try:
                worker_id = int(worker_id_var.get())
                job_title = job_title_var.get().strip()
                contract = contract_var.get().strip()
                wage_increase = float(wage_var.get() or 0)

                if not job_title or not contract:
                    messagebox.showerror("Error", "Please fill in all required fields")
                    return

                query = "CALL update_worker_contract(%s, %s, %s, %s)"
                db_manager.execute_query(query, (worker_id, job_title, contract, wage_increase))

                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, "UPDATE WORKER CONTRACT PROCEDURE\n")
                self.results_text.insert(tk.END, "=" * 80 + "\n")
                self.results_text.insert(tk.END, f"Executed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                self.results_text.insert(tk.END, f"Worker ID: {worker_id}\n")
                self.results_text.insert(tk.END, f"New Job Title: {job_title}\n")
                self.results_text.insert(tk.END, f"New Contract: {contract}\n")
                self.results_text.insert(tk.END, f"Wage Increase: ${wage_increase:.2f}\n")
                self.results_text.insert(tk.END, "\nProcedure executed successfully!\n")

                self.update_status("Worker contract updated")
                dialog.destroy()

            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to execute procedure: {str(e)}")
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, f"ERROR: {str(e)}\n")

        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Execute", command=execute_procedure,
                  bg="#27ae60", fg="white", width=10).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy,
                  bg="#95a5a6", fg="white", width=10).pack(side="left", padx=5)

    def proc_process_equipment_orders(self):
        """Execute process equipment orders procedure"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Process Equipment Orders")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()

        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))

        # Input fields
        tk.Label(dialog, text="Supplier ID:", font=("Arial", 12)).pack(pady=10)
        supplier_id_var = tk.StringVar()
        tk.Entry(dialog, textvariable=supplier_id_var, font=("Arial", 11), width=20).pack(pady=5)

        tk.Label(dialog, text="Order Date (YYYY-MM-DD):", font=("Arial", 12)).pack(pady=5)
        order_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        tk.Entry(dialog, textvariable=order_date_var, font=("Arial", 11), width=20).pack(pady=5)

        def execute_procedure():
            try:
                supplier_id = int(supplier_id_var.get())
                order_date = order_date_var.get().strip()

                query = "CALL process_equipment_orders(%s, %s)"
                db_manager.execute_query(query, (supplier_id, order_date))

                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, "PROCESS EQUIPMENT ORDERS PROCEDURE\n")
                self.results_text.insert(tk.END, "=" * 80 + "\n")
                self.results_text.insert(tk.END, f"Executed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                self.results_text.insert(tk.END, f"Supplier ID: {supplier_id}\n")
                self.results_text.insert(tk.END, f"Order Date: {order_date}\n")
                self.results_text.insert(tk.END, "\nProcedure executed successfully!\n")
                self.results_text.insert(tk.END, "Check database logs for detailed output.\n")

                self.update_status("Equipment orders processed")
                dialog.destroy()

            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to execute procedure: {str(e)}")
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, f"ERROR: {str(e)}\n")

        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Execute", command=execute_procedure,
                  bg="#27ae60", fg="white", width=10).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy,
                  bg="#95a5a6", fg="white", width=10).pack(side="left", padx=5)