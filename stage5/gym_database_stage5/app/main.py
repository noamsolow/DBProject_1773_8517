# improved_main_application.py - Better Main GUI Application
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import traceback
from datetime import datetime

# Import our real modules
from app.database import db_manager
from worker_operations import WorkerOperations, WorkerDialog
from app.supplier_operations import SupplierOperations, SupplierDialog
from equipment_operations import EquipmentOperations, EquipmentDialog
from app.equipment_supplier_operations import EquipmentSupplierOperations, EquipmentSupplierDialog


class SportsInstituteApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sports Institute Management System")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f8f9fa")

        # Set window icon and properties
        self.root.resizable(True, True)
        self.root.minsize(1000, 600)

        # Initialize operations
        self.worker_ops = WorkerOperations()
        self.supplier_ops = SupplierOperations()
        self.equipment_ops = EquipmentOperations()
        self.es_ops = EquipmentSupplierOperations()

        # Connect to database
        if not self.connect_database():
            return

        # Setup styles
        self.setup_styles()

        # Create main interface
        self.create_main_interface()

    def connect_database(self):
        """Connect to database with error handling"""
        try:
            if db_manager.connect():
                return True
            else:
                messagebox.showerror("Database Error",
                                     "Failed to connect to database. Please check your connection settings.")
                self.root.quit()
                return False
        except Exception as e:
            messagebox.showerror("Database Error", f"Connection error: {str(e)}")
            self.root.quit()
            return False

    def setup_styles(self):
        """Setup custom styles for better appearance"""
        style = ttk.Style()

        # Configure treeview style
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="#2c3e50",
                        rowheight=25,
                        fieldbackground="#ffffff")
        style.configure("Treeview.Heading",
                        background="#34495e",
                        foreground="white",
                        relief="flat")
        style.map("Treeview.Heading",
                  background=[('active', '#2c3e50')])

    def create_main_interface(self):
        """Create the main application interface"""
        # Create main container
        main_container = tk.Frame(self.root, bg="#f8f9fa")
        main_container.pack(fill="both", expand=True)

        # Create header
        self.create_header(main_container)

        # Create navigation sidebar
        self.create_sidebar(main_container)

        # Create main content area
        self.create_content_area(main_container)

        # Create status bar
        self.create_status_bar(main_container)

        # Show welcome screen initially
        self.show_welcome_screen()

    def create_header(self, parent):
        """Create application header"""
        header_frame = tk.Frame(parent, bg="#2c3e50", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        # Title
        title_label = tk.Label(header_frame,
                               text="Sports Institute Management System",
                               font=("Arial", 20, "bold"),
                               fg="white", bg="#2c3e50")
        title_label.pack(side="left", padx=20, pady=20)

        # Current time
        self.time_label = tk.Label(header_frame,
                                   text="",
                                   font=("Arial", 10),
                                   fg="#ecf0f1", bg="#2c3e50")
        self.time_label.pack(side="right", padx=20, pady=20)

        # Update time
        self.update_time()

    def create_sidebar(self, parent):
        """Create navigation sidebar"""
        sidebar_frame = tk.Frame(parent, bg="#34495e", width=250)
        sidebar_frame.pack(side="left", fill="y")
        sidebar_frame.pack_propagate(False)

        # Navigation buttons
        nav_buttons = [
            ("🏠 Home", self.show_welcome_screen, "#3498db"),
            ("👥 Workers", self.show_workers_screen, "#27ae60"),
            ("🏭 Suppliers", self.show_suppliers_screen, "#9b59b6"),
            ("⚙️ Equipment", self.show_equipment_screen, "#e74c3c"),
            ("🔗 Supplier Equipment", self.show_relationships_screen, "#f39c12"),
            ("📊 Reports", self.show_reports_screen, "#16a085"),
            ("❌ Exit", self.exit_application, "#95a5a6")
        ]

        # Add some spacing at top
        tk.Label(sidebar_frame, text="", bg="#34495e", height=2).pack()

        self.nav_buttons = {}
        for text, command, color in nav_buttons:
            btn = tk.Button(sidebar_frame,
                            text=text,
                            command=command,
                            font=("Arial", 12, "bold"),
                            bg=color,
                            fg="white",
                            bd=0,
                            relief="flat",
                            width=25,
                            height=2,
                            cursor="hand2")
            btn.pack(pady=5, padx=10, fill="x")

            # Add hover effects
            btn.bind("<Enter>", lambda e, b=btn, c=color: self.on_button_hover(b, c))
            btn.bind("<Leave>", lambda e, b=btn, c=color: self.on_button_leave(b, c))

            self.nav_buttons[text] = btn

    def create_content_area(self, parent):
        """Create main content area"""
        self.content_frame = tk.Frame(parent, bg="#ffffff")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = tk.Frame(parent, bg="#ecf0f1", height=30)
        status_frame.pack(side="bottom", fill="x")
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(status_frame,
                                     text="Ready",
                                     font=("Arial", 9),
                                     fg="#2c3e50", bg="#ecf0f1")
        self.status_label.pack(side="left", padx=10, pady=5)

        # Database connection status
        self.db_status_label = tk.Label(status_frame,
                                        text="Database: Connected",
                                        font=("Arial", 9),
                                        fg="#27ae60", bg="#ecf0f1")
        self.db_status_label.pack(side="right", padx=10, pady=5)

    def on_button_hover(self, button, original_color):
        """Button hover effect"""
        # Darken the color slightly
        darker_colors = {
            "#3498db": "#2980b9",
            "#27ae60": "#229954",
            "#9b59b6": "#8e44ad",
            "#e74c3c": "#c0392b",
            "#f39c12": "#e67e22",
            "#16a085": "#138d75",
            "#95a5a6": "#7f8c8d"
        }
        button.config(bg=darker_colors.get(original_color, original_color))

    def on_button_leave(self, button, original_color):
        """Button leave effect"""
        button.config(bg=original_color)

    def update_time(self):
        """Update current time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)

    def update_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=message)
        self.root.after(3000, lambda: self.status_label.config(text="Ready"))

    def clear_content(self):
        """Clear the content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_welcome_screen(self):
        """Show welcome/dashboard screen"""
        self.clear_content()

        # Welcome header
        welcome_label = tk.Label(self.content_frame,
                                 text="Welcome to Sports Institute Management",
                                 font=("Arial", 24, "bold"),
                                 fg="#2c3e50", bg="#ffffff")
        welcome_label.pack(pady=30)

        # Dashboard cards
        cards_frame = tk.Frame(self.content_frame, bg="#ffffff")
        cards_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Get statistics
        stats = self.get_dashboard_stats()

        # Create dashboard cards
        cards = [
            ("Total Workers", stats['workers'], "#3498db", "👥"),
            ("Total Suppliers", stats['suppliers'], "#9b59b6", "🏭"),
            ("Total Equipment", stats['equipment'], "#e74c3c", "⚙️"),
            ("Total Relationships", stats['relationships'], "#f39c12", "🔗")
        ]

        for i, (title, count, color, icon) in enumerate(cards):
            self.create_dashboard_card(cards_frame, title, count, color, icon, i)

        # Quick actions
        self.create_quick_actions(cards_frame)

        self.update_status("Dashboard loaded")

    def create_dashboard_card(self, parent, title, count, color, icon, index):
        """Create a dashboard statistics card"""
        row = index // 2
        col = index % 2

        card_frame = tk.Frame(parent, bg=color, relief="raised", bd=2)
        card_frame.grid(row=row, column=col, padx=20, pady=20, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)

        # Icon
        icon_label = tk.Label(card_frame, text=icon, font=("Arial", 30),
                              fg="white", bg=color)
        icon_label.pack(pady=10)

        # Count
        count_label = tk.Label(card_frame, text=str(count), font=("Arial", 24, "bold"),
                               fg="white", bg=color)
        count_label.pack()

        # Title
        title_label = tk.Label(card_frame, text=title, font=("Arial", 12),
                               fg="white", bg=color)
        title_label.pack(pady=(0, 15))

    def create_quick_actions(self, parent):
        """Create quick action buttons"""
        actions_frame = tk.LabelFrame(parent, text="Quick Actions",
                                      font=("Arial", 14, "bold"),
                                      fg="#2c3e50", bg="#ffffff")
        actions_frame.grid(row=2, column=0, columnspan=2, pady=30, padx=20, sticky="ew")

        quick_buttons = [
            ("Add New Worker", self.quick_add_worker, "#27ae60"),
            ("Add New Equipment", self.quick_add_equipment, "#e74c3c"),
            ("View Reports", self.show_reports_screen, "#16a085"),
            ("Manage Supplied Equipment", self.show_relationships_screen, "#f39c12")
        ]

        for i, (text, command, color) in enumerate(quick_buttons):
            btn = tk.Button(actions_frame, text=text, command=command,
                            font=("Arial", 11, "bold"), bg=color, fg="white",
                            width=20, height=2, cursor="hand2")
            btn.grid(row=0, column=i, padx=10, pady=15)

    def get_dashboard_stats(self):
        """Get statistics for dashboard"""
        stats = {'workers': 0, 'suppliers': 0, 'equipment': 0, 'Supplied Equipment': 0}

        try:
            # Count workers
            result = db_manager.execute_query("SELECT COUNT(*) FROM worker", fetch='one')
            stats['workers'] = result[0] if result else 0

            # Count suppliers
            result = db_manager.execute_query("SELECT COUNT(*) FROM supplier", fetch='one')
            stats['suppliers'] = result[0] if result else 0

            # Count equipment
            result = db_manager.execute_query("SELECT COUNT(*) FROM equipment", fetch='one')
            stats['equipment'] = result[0] if result else 0

            # Count relationships
            result = db_manager.execute_query("SELECT COUNT(*) FROM equipment_supplier", fetch='one')
            stats['relationships'] = result[0] if result else 0

        except Exception as e:
            print(f"Error getting stats: {e}")

        return stats

    def show_workers_screen(self):
        """Show workers management screen"""
        self.clear_content()

        # Header
        header_frame = tk.Frame(self.content_frame, bg="#ffffff")
        header_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(header_frame, text="Worker Management",
                 font=("Arial", 18, "bold"), fg="#2c3e50", bg="#ffffff").pack(side="left")

        # Search bar
        search_frame = tk.Frame(self.content_frame, bg="#ffffff")
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="Search:", font=("Arial", 11), bg="#ffffff").pack(side="left")
        self.worker_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.worker_search_var, width=30, font=("Arial", 10))
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", lambda e: self.search_workers())


        tk.Button(search_frame, text="Clear", command=self.refresh_workers,
                  font=("Arial", 10), bg="#95a5a6", fg="white").pack(side="left", padx=5)

        # Control buttons
        btn_frame = tk.Frame(header_frame, bg="#ffffff")
        btn_frame.pack(side="right")

        buttons = [
            ("Add Worker", self.add_worker, "#27ae60"),
            ("Edit Worker", self.edit_worker, "#f39c12"),
            ("Delete Worker", self.delete_worker, "#e74c3c"),
            ("Refresh", self.refresh_workers, "#3498db")
        ]

        for text, command, color in buttons:
            tk.Button(btn_frame, text=text, command=command,
                      font=("Arial", 10, "bold"), bg=color, fg="white",
                      width=12, cursor="hand2").pack(side="left", padx=5)

        # Workers table
        self.create_workers_table()
        self.refresh_workers()
        self.update_status("Workers screen loaded")

    def create_workers_table(self):
        """Create workers table"""
        table_frame = tk.Frame(self.content_frame, bg="#ffffff")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Apply style for black header text
        style = ttk.Style()
        style.theme_use("clam")  # Use a theme that allows styling
        style.configure("Treeview.Heading", foreground="black", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)

        # Columns
        columns = ("PID", "First Name", "Last Name", "Job", "Contract", "Date of Deployment")
        self.workers_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # Configure columns
        widths = [80, 120, 120, 150, 120, 130]
        for i, col in enumerate(columns):
            self.workers_tree.heading(col, text=col)
            self.workers_tree.column(col, width=widths[i], minwidth=50)

        # Scrollbars
        v_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.workers_tree.yview)
        h_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.workers_tree.xview)
        self.workers_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Pack elements
        self.workers_tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")

        # Double-click to edit
        self.workers_tree.bind("<Double-1>", lambda e: self.edit_worker())

    def search_workers(self):
        """Search workers by name or job"""
        query_text = self.worker_search_var.get().strip().lower()
        if not query_text:
            self.refresh_workers()
            return

        try:
            all_workers = self.worker_ops.get_all_workers()
            filtered = [
                worker for worker in all_workers
                if query_text in str(worker[0]).lower() or
                   query_text in str(worker[1]).lower() or# first name
                   query_text in str(worker[2]).lower() or  # last name
                   query_text in str(worker[3]).lower() or
                   query_text in str(worker[4]).lower() or
                   query_text in str(worker[5]).lower()  # job
            ]

            self.workers_tree.delete(*self.workers_tree.get_children())
            for worker in filtered:
                self.workers_tree.insert("", "end", values=worker)

            self.update_status(f"Found {len(filtered)} result(s) for '{query_text}'")

        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")

    def show_suppliers_screen(self):
        """Show suppliers management screen"""
        self.clear_content()

        # Header
        header_frame = tk.Frame(self.content_frame, bg="#ffffff")
        header_frame.pack(fill="x", padx=10, pady=10)
        # Add this under the header
        search_frame = tk.Frame(self.content_frame, bg="#ffffff")
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="Search:", font=("Arial", 11), bg="#ffffff").pack(side="left")
        self.supplier_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.supplier_search_var, width=30, font=("Arial", 10))
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", lambda e: self.search_suppliers())

        tk.Button(search_frame, text="Clear", command=self.refresh_suppliers,
                  font=("Arial", 10), bg="#95a5a6", fg="white").pack(side="left", padx=5)

        tk.Label(header_frame, text="Supplier Management",
                 font=("Arial", 18, "bold"), fg="#2c3e50", bg="#ffffff").pack(side="left")

        # Control buttons
        btn_frame = tk.Frame(header_frame, bg="#ffffff")
        btn_frame.pack(side="right")

        buttons = [
            ("Add Supplier", self.add_supplier, "#27ae60"),
            ("Edit Supplier", self.edit_supplier, "#f39c12"),
            ("Delete Supplier", self.delete_supplier, "#e74c3c"),
            ("Refresh", self.refresh_suppliers, "#3498db")
        ]

        for text, command, color in buttons:
            tk.Button(btn_frame, text=text, command=command,
                      font=("Arial", 10, "bold"), bg=color, fg="white",
                      width=12, cursor="hand2").pack(side="left", padx=5)

        # Suppliers table
        self.create_suppliers_table()
        self.refresh_suppliers()
        self.update_status("Suppliers screen loaded")

    def search_suppliers(self):
        """Search suppliers live"""
        query = self.supplier_search_var.get().strip().lower()
        if not query:
            self.refresh_suppliers()
            return

        try:
            all_suppliers = self.supplier_ops.get_all_suppliers()
            filtered = [
                s for s in all_suppliers
                if query in str(s[1]).lower() or  # First Name
                   query in str(s[2]).lower() or  # Last Name
                   query in str(s[4]).lower()  # Address
            ]
            self.suppliers_tree.delete(*self.suppliers_tree.get_children())
            for s in filtered:
                self.suppliers_tree.insert("", "end", values=s)

            self.update_status(f"{len(filtered)} supplier(s) matched")
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")

    def create_suppliers_table(self):
        """Create suppliers table"""
        table_frame = tk.Frame(self.content_frame, bg="#ffffff")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("Supplier ID", "First Name", "Last Name", "Date of Birth", "Address", "Phone", "Email")

        self.suppliers_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # Configure columns
        widths = [80, 120, 120, 100, 150, 120, 150]
        for i, col in enumerate(columns):
            self.suppliers_tree.heading(col, text=col)
            self.suppliers_tree.column(col, width=widths[i], minwidth=50)

        # Scrollbars
        v_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.suppliers_tree.yview)
        h_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.suppliers_tree.xview)
        self.suppliers_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.suppliers_tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")

        self.suppliers_tree.bind("<Double-1>", lambda e: self.edit_supplier())

    def show_equipment_screen(self):
        """Show equipment management screen"""
        self.clear_content()

        # Header
        header_frame = tk.Frame(self.content_frame, bg="#ffffff")
        header_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(header_frame, text="Equipment Management",
                 font=("Arial", 18, "bold"), fg="#2c3e50", bg="#ffffff").pack(side="left")

        # Control buttons
        btn_frame = tk.Frame(header_frame, bg="#ffffff")
        btn_frame.pack(side="right")

        # Add this under the header
        search_frame = tk.Frame(self.content_frame, bg="#ffffff")
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="Search:", font=("Arial", 11), bg="#ffffff").pack(side="left")
        self.equipment_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.equipment_search_var, width=30, font=("Arial", 10))
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", lambda e: self.search_equipment())

        tk.Button(search_frame, text="Clear", command=self.refresh_equipment,
                  font=("Arial", 10), bg="#95a5a6", fg="white").pack(side="left", padx=5)

        buttons = [
            ("Add Equipment", self.add_equipment, "#27ae60"),
            ("Edit Equipment", self.edit_equipment, "#f39c12"),
            ("Delete Equipment", self.delete_equipment, "#e74c3c"),
            ("Refresh", self.refresh_equipment, "#3498db")
        ]

        for text, command, color in buttons:
            tk.Button(btn_frame, text=text, command=command,
                      font=("Arial", 10, "bold"), bg=color, fg="white",
                      width=12, cursor="hand2").pack(side="left", padx=5)

        # Equipment table
        self.create_equipment_table()
        self.refresh_equipment()
        self.update_status("Equipment screen loaded")

    def create_equipment_table(self):
        """Create equipment table"""
        table_frame = tk.Frame(self.content_frame, bg="#ffffff")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("Equipment ID", "Name", "Category", "Purchase Date", "Warranty Expiry", "Brand")

        self.equipment_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # Configure columns
        widths = [100, 150, 120, 120, 120, 120]
        for i, col in enumerate(columns):
            self.equipment_tree.heading(col, text=col)
            self.equipment_tree.column(col, width=widths[i], minwidth=50)

        # Scrollbars
        v_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.equipment_tree.yview)
        h_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.equipment_tree.xview)
        self.equipment_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.equipment_tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")

        self.equipment_tree.bind("<Double-1>", lambda e: self.edit_equipment())

    def search_equipment(self):
        """Live search for equipment"""
        query = self.equipment_search_var.get().strip().lower()
        if not query:
            self.refresh_equipment()
            return

        try:
            all_eq = self.equipment_ops.get_all_equipment()
            filtered = [
                eq for eq in all_eq
                if query in str(eq[1]).lower() or  # Name
                   query in str(eq[2]).lower() or  # Category
                   query in str(eq[5]).lower()  # Brand
            ]
            self.equipment_tree.delete(*self.equipment_tree.get_children())
            for eq in filtered:
                self.equipment_tree.insert("", "end", values=eq)

            self.update_status(f"{len(filtered)} equipment item(s) matched")
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")

    def show_relationships_screen(self):
        """Show equipment-supplier relationships screen"""
        self.clear_content()

        # Header
        header_frame = tk.Frame(self.content_frame, bg="#ffffff")
        header_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(header_frame, text="Equipment-Supplier Relationships",
                 font=("Arial", 18, "bold"), fg="#2c3e50", bg="#ffffff").pack(side="left")

        # Control buttons
        btn_frame = tk.Frame(header_frame, bg="#ffffff")
        btn_frame.pack(side="right")
        # Add this under the header
        search_frame = tk.Frame(self.content_frame, bg="#ffffff")
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="Search:", font=("Arial", 11), bg="#ffffff").pack(side="left")
        self.relationship_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.relationship_search_var, width=30, font=("Arial", 10))
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", lambda e: self.search_relationships())

        tk.Button(search_frame, text="Clear", command=self.refresh_relationships,
                  font=("Arial", 10), bg="#95a5a6", fg="white").pack(side="left", padx=5)

        buttons = [
            ("Add Relationship", self.add_relationship, "#27ae60"),
            ("Edit Relationship", self.edit_relationship, "#f39c12"),
            ("Delete Relationship", self.delete_relationship, "#e74c3c"),
            ("Refresh", self.refresh_relationships, "#3498db")
        ]

        for text, command, color in buttons:
            tk.Button(btn_frame, text=text, command=command,
                      font=("Arial", 10, "bold"), bg=color, fg="white",
                      width=15, cursor="hand2").pack(side="left", padx=5)

        # Relationships table
        self.create_relationships_table()
        self.refresh_relationships()
        self.update_status("Relationships screen loaded")

    def create_relationships_table(self):
        """Create relationships table"""
        table_frame = tk.Frame(self.content_frame, bg="#ffffff")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("Eq. ID", "Equipment", "Category", "Person ID", "Person Name", "Quantity", "Supply Date")

        self.relationships_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # Configure columns
        widths = [60, 150, 100, 80, 150, 80, 100, 80]
        for i, col in enumerate(columns):
            self.relationships_tree.heading(col, text=col)
            self.relationships_tree.column(col, width=widths[i], minwidth=50)

        # Scrollbars
        v_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.relationships_tree.yview)
        h_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.relationships_tree.xview)
        self.relationships_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.relationships_tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")

        self.relationships_tree.bind("<Double-1>", lambda e: self.edit_relationship())

    def search_relationships(self):
        """Live search for equipment-supplier relationships"""
        query = self.relationship_search_var.get().strip().lower()
        if not query:
            self.refresh_relationships()
            return

        try:
            all_rels = self.es_ops.get_all_equipment_suppliers()
            filtered = [
                rel for rel in all_rels
                if query in str(rel[1]).lower() or  # Equipment Name
                   query in str(rel[2]).lower() or  # Category
                   query in str(rel[4]).lower()  # Person Name
            ]
            self.relationships_tree.delete(*self.relationships_tree.get_children())
            for rel in filtered:
                self.relationships_tree.insert("", "end", values=rel)

            self.update_status(f"{len(filtered)} relationship(s) matched")
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")

    def show_reports_screen(self):
        """Show reports and analytics screen"""
        self.clear_content()

        # Header
        header_frame = tk.Frame(self.content_frame, bg="#ffffff")
        header_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(header_frame, text="Reports & Analytics",
                 font=("Arial", 18, "bold"), fg="#2c3e50", bg="#ffffff").pack(side="left")

        # Standard Report buttons
        reports_frame = tk.LabelFrame(self.content_frame, text="Standard Reports",
                                      font=("Arial", 12, "bold"), fg="#2c3e50", bg="#ffffff")
        reports_frame.pack(fill="x", padx=10, pady=10)

        report_buttons = [
            ("Equipment by Person", self.report_equipment_by_person, "#16a085"),
            ("Person Summary Report", self.report_person_summary, "#16a085"),
            ("Equipment Statistics", self.report_equipment_stats, "#16a085"),
            ("Supply Timeline", self.report_supply_timeline, "#16a085")
        ]

        for i, (text, command, color) in enumerate(report_buttons):
            btn = tk.Button(reports_frame, text=text, command=command,
                            font=("Arial", 11, "bold"), bg=color, fg="white",
                            width=20, height=2, cursor="hand2")
            btn.grid(row=i // 2, column=i % 2, padx=10, pady=10)

        # Advanced Functions/Procedures Section
        advanced_frame = tk.LabelFrame(self.content_frame, text="Advanced Functions & Procedures",
                                       font=("Arial", 12, "bold"), fg="#2c3e50", bg="#ffffff")
        advanced_frame.pack(fill="x", padx=10, pady=10)

        # Function buttons
        func_buttons = [
            ("Worker Shift Summary", self.func_worker_shift_summary, "#8e44ad"),
            ("Equipment Maintenance Status", self.func_equipment_maintenance_status, "#8e44ad"),
            ("Update Worker Contract", self.proc_update_worker_contract, "#e67e22"),
            ("Process Equipment Orders", self.proc_process_equipment_orders, "#e67e22")
        ]

        for i, (text, command, color) in enumerate(func_buttons):
            btn = tk.Button(advanced_frame, text=text, command=command,
                            font=("Arial", 11, "bold"), bg=color, fg="white",
                            width=20, height=2, cursor="hand2")
            btn.grid(row=i // 2, column=i % 2, padx=10, pady=10)

        # Results area
        results_frame = tk.LabelFrame(self.content_frame, text="Report Results",
                                      font=("Arial", 12, "bold"), fg="#2c3e50", bg="#ffffff")
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.results_text = tk.Text(results_frame, font=("Consolas", 10), bg="#f8f9fa",
                                    wrap="none", relief="flat", bd=5)

        # Scrollbars
        v_scroll = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        h_scroll = ttk.Scrollbar(results_frame, orient="horizontal", command=self.results_text.xview)
        self.results_text.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.results_text.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")

        self.update_status("Reports screen loaded")

    # CRUD Operations
    def refresh_workers(self):
        """Refresh workers table"""
        try:
            if hasattr(self, 'workers_tree'):
                for item in self.workers_tree.get_children():
                    self.workers_tree.delete(item)

                workers = self.worker_ops.get_all_workers()
                for worker in workers:
                    self.workers_tree.insert("", "end", values=worker)

                self.update_status(f"Loaded {len(workers)} workers")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh workers: {str(e)}")

    def add_worker(self):
        """Add new worker"""
        dialog = WorkerDialog(self.root, "Add New Worker")
        self.root.wait_window(dialog.dialog)

        if dialog.result:
            if self.worker_ops.add_worker(dialog.result):
                messagebox.showinfo("Success", "Worker added successfully!")
                self.refresh_workers()
                self.update_status("Worker added")

    def edit_worker(self):
        """Edit selected worker"""
        if not hasattr(self, 'workers_tree'):
            return

        selection = self.workers_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a worker to edit")
            return

        item = self.workers_tree.item(selection[0])
        worker_data = item['values']
        worker_pid = worker_data[0]

        detailed_data = self.worker_ops.get_worker_details(worker_pid)
        if detailed_data:
            dialog = WorkerDialog(self.root, "Edit Worker", detailed_data)
            self.root.wait_window(dialog.dialog)

            if dialog.result:
                if self.worker_ops.update_worker(worker_pid, dialog.result):
                    messagebox.showinfo("Success", "Worker updated successfully!")
                    self.refresh_workers()
                    self.update_status("Worker updated")

    def delete_worker(self):
        """Delete selected worker"""
        if not hasattr(self, 'workers_tree'):
            return

        selection = self.workers_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a worker to delete")
            return

        item = self.workers_tree.item(selection[0])
        worker_data = item['values']
        worker_pid = worker_data[0]
        worker_name = f"{worker_data[1]} {worker_data[2]}"

        if messagebox.askyesno("Confirm Delete", f"Delete worker {worker_name}?"):
            if self.worker_ops.delete_worker(worker_pid):
                messagebox.showinfo("Success", "Worker deleted successfully!")
                self.refresh_workers()
                self.update_status("Worker deleted")

    def refresh_suppliers(self):
        """Refresh suppliers table"""
        try:
            if hasattr(self, 'suppliers_tree'):
                for item in self.suppliers_tree.get_children():
                    self.suppliers_tree.delete(item)

                suppliers = self.supplier_ops.get_all_suppliers()
                for supplier in suppliers:
                    self.suppliers_tree.insert("", "end", values=supplier)

                self.update_status(f"Loaded {len(suppliers)} suppliers")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh suppliers: {str(e)}")

    def add_supplier(self):
        """Add new supplier"""
        dialog = SupplierDialog(self.root, "Add New Supplier")
        self.root.wait_window(dialog.dialog)

        if dialog.result:
            if self.supplier_ops.add_supplier(dialog.result):
                messagebox.showinfo("Success", "Supplier added successfully!")
                self.refresh_suppliers()
                self.update_status("Supplier added")

    def edit_supplier(self):
        """Edit selected supplier"""
        if not hasattr(self, 'suppliers_tree'):
            return

        selection = self.suppliers_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a supplier to edit")
            return

        item = self.suppliers_tree.item(selection[0])
        supplier_data = item['values']
        supplier_id = supplier_data[0]

        detailed_data = self.supplier_ops.get_supplier_details(supplier_id)
        if detailed_data:
            dialog = SupplierDialog(self.root, "Edit Supplier", detailed_data)
            self.root.wait_window(dialog.dialog)

            if dialog.result:
                if self.supplier_ops.update_supplier(supplier_id, dialog.result):
                    messagebox.showinfo("Success", "Supplier updated successfully!")
                    self.refresh_suppliers()
                    self.update_status("Supplier updated")

    def delete_supplier(self):
        """Delete selected supplier"""
        if not hasattr(self, 'suppliers_tree'):
            return

        selection = self.suppliers_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a supplier to delete")
            return

        item = self.suppliers_tree.item(selection[0])
        supplier_data = item['values']
        supplier_id = supplier_data[0]
        supplier_name = f"{supplier_data[1]} {supplier_data[2]}"

        if messagebox.askyesno("Confirm Delete", f"Delete supplier {supplier_name}?"):
            if self.supplier_ops.delete_supplier(supplier_id):
                messagebox.showinfo("Success", "Supplier deleted successfully!")
                self.refresh_suppliers()
                self.update_status("Supplier deleted")

    def refresh_equipment(self):
        """Refresh equipment table"""
        try:
            if hasattr(self, 'equipment_tree'):
                for item in self.equipment_tree.get_children():
                    self.equipment_tree.delete(item)

                equipment = self.equipment_ops.get_all_equipment()
                for item in equipment:
                    self.equipment_tree.insert("", "end", values=item)

                self.update_status(f"Loaded {len(equipment)} equipment items")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh equipment: {str(e)}")

    def add_equipment(self):
        """Add new equipment"""
        dialog = EquipmentDialog(self.root, "Add New Equipment")
        self.root.wait_window(dialog.dialog)

        if dialog.result:
            if self.equipment_ops.add_equipment(dialog.result):
                messagebox.showinfo("Success", "Equipment added successfully!")
                self.refresh_equipment()
                self.update_status("Equipment added")

    def edit_equipment(self):
        """Edit selected equipment"""
        if not hasattr(self, 'equipment_tree'):
            return

        selection = self.equipment_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select equipment to edit")
            return

        item = self.equipment_tree.item(selection[0])
        equipment_data = item['values']

        dialog = EquipmentDialog(self.root, "Edit Equipment", equipment_data)
        self.root.wait_window(dialog.dialog)

        if dialog.result:
            if self.equipment_ops.update_equipment(equipment_data[0], dialog.result):
                messagebox.showinfo("Success", "Equipment updated successfully!")
                self.refresh_equipment()
                self.update_status("Equipment updated")

    def delete_equipment(self):
        """Delete selected equipment"""
        if not hasattr(self, 'equipment_tree'):
            return

        selection = self.equipment_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select equipment to delete")
            return

        item = self.equipment_tree.item(selection[0])
        equipment_data = item['values']
        equipment_id = equipment_data[0]
        equipment_name = equipment_data[1]

        if messagebox.askyesno("Confirm Delete", f"Delete equipment {equipment_name}?"):
            if self.equipment_ops.delete_equipment(equipment_id):
                messagebox.showinfo("Success", "Equipment deleted successfully!")
                self.refresh_equipment()
                self.update_status("Equipment deleted")

    def refresh_relationships(self):
        """Refresh relationships table"""
        try:
            if hasattr(self, 'relationships_tree'):
                for item in self.relationships_tree.get_children():
                    self.relationships_tree.delete(item)

                relationships = self.es_ops.get_all_equipment_suppliers()
                for relationship in relationships:
                    self.relationships_tree.insert("", "end", values=relationship)

                self.update_status(f"Loaded {len(relationships)} relationships")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh relationships: {str(e)}")

    def add_relationship(self):
        """Add new equipment-supplier relationship"""
        dialog = EquipmentSupplierDialog(self.root, "Add New Relationship")
        self.root.wait_window(dialog.dialog)

        if dialog.result:
            if self.es_ops.add_equipment_supplier(dialog.result):
                messagebox.showinfo("Success", "Relationship added successfully!")
                self.refresh_relationships()
                self.update_status("Relationship added")

    def edit_relationship(self):
        """Edit selected relationship"""
        if not hasattr(self, 'relationships_tree'):
            return

        selection = self.relationships_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a relationship to edit")
            return

        item = self.relationships_tree.item(selection[0])
        relationship_data = item['values']

        dialog = EquipmentSupplierDialog(self.root, "Edit Relationship", relationship_data)
        self.root.wait_window(dialog.dialog)

        if dialog.result:
            if self.es_ops.update_equipment_supplier(relationship_data, dialog.result):
                messagebox.showinfo("Success", "Relationship updated successfully!")
                self.refresh_relationships()
                self.update_status("Relationship updated")

    def delete_relationship(self):
        """Delete selected relationship"""
        if not hasattr(self, 'relationships_tree'):
            return

        selection = self.relationships_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a relationship to delete")
            return

        item = self.relationships_tree.item(selection[0])
        relationship_data = item['values']
        equipment_id = relationship_data[0]
        pid = relationship_data[3]
        equipment_name = relationship_data[1]
        person_name = relationship_data[4]

        if messagebox.askyesno("Confirm Delete",
                               f"Delete relationship between {equipment_name} and {person_name}?"):
            if self.es_ops.delete_equipment_supplier(equipment_id, pid):
                messagebox.showinfo("Success", "Relationship deleted successfully!")
                self.refresh_relationships()
                self.update_status("Relationship deleted")

    # Quick Actions
    def quick_add_worker(self):
        """Quick add worker from dashboard"""
        self.show_workers_screen()
        self.add_worker()

    def quick_add_equipment(self):
        """Quick add equipment from dashboard"""
        self.show_equipment_screen()
        self.add_equipment()

    # Report Functions
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

    # Advanced Functions and Procedures
    def func_worker_shift_summary(self):
        """Execute worker shift summary function"""
        # Input dialog for worker ID
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
            # For PostgreSQL ref cursor, we need to handle it differently
            # This is a simplified version - you may need to adjust based on your database setup
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
        # Create input dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Update Worker Contract")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog
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

                # Execute the procedure
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
        # Create input dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Process Equipment Orders")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog
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

                # Execute the procedure
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

    def exit_application(self):
        """Exit the application"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            try:
                if db_manager.connection:
                    db_manager.disconnect()
            except:
                pass
            self.root.quit()

    def run(self):
        """Run the application"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Application error: {e}")
            traceback.print_exc()
        finally:
            try:
                if db_manager.connection:
                    db_manager.disconnect()
            except:
                pass


if __name__ == "__main__":
    try:
        app = SportsInstituteApp()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        traceback.print_exc()