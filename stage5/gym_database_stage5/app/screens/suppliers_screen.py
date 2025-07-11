# screens/suppliers_screen.py
import tkinter as tk
from tkinter import ttk, messagebox
from app.operations.supplier_operations import SupplierOperations, SupplierDialog


class SuppliersScreen:
    def __init__(self, app):
        self.app = app
        self.root = app.root
        self.content_frame = app.content_frame
        self.update_status = app.update_status
        self.supplier_ops = SupplierOperations()
        self.supplier_search_var = None
        self.suppliers_tree = None

    def show_suppliers_screen(self):
        """Show suppliers management screen"""
        self.app.clear_content()
        self.content_frame.configure(bg="#f2ffed")


        # Header
        header_frame = tk.Frame(self.content_frame, bg="#cef5cb")
        header_frame.pack(fill="x", padx=10, pady=10)

        # Search bar
        search_frame = tk.Frame(self.content_frame, bg="#cef5cb")
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="Search:", font=("Arial", 11), bg="#cef5cb").pack(side="left")
        self.supplier_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.supplier_search_var, width=30, font=("Arial", 10))
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", lambda e: self.search_suppliers())

        tk.Button(search_frame, text="Clear", command=self.refresh_suppliers,
                  font=("Arial", 10), bg="#95a5a6", fg="white").pack(side="left", padx=5)

        tk.Label(header_frame, text="Supplier Management",
                 font=("Arial", 18, "bold"), fg="#022903", bg="#cef5cb").pack(side="left")

        # Control buttons
        btn_frame = tk.Frame(header_frame, bg="#a6f7a9")
        btn_frame.pack(side="right")

        buttons = [
            ("Add Supplier", self.add_supplier, "#09610b"),
            ("Edit Supplier", self.edit_supplier, "#0e7d10"),
            ("Delete Supplier", self.delete_supplier, "#13a815"),
            ("Refresh", self.refresh_suppliers, "#21db24")
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
                if query in str(s[0]).lower() or # id
                   query in str(s[1]).lower() or  # First Name
                   query in str(s[2]).lower() or  # Last Name
                   query in str(s[3]).lower() or # DOB
                    query in str(s[4]).lower() or  # address
                    query in str(s[5]).lower() or # phone
                   query in str(s[6]).lower()   # Email

            ]
            self.suppliers_tree.delete(*self.suppliers_tree.get_children())
            for s in filtered:
                self.suppliers_tree.insert("", "end", values=s)

            self.update_status(f"{len(filtered)} supplier(s) matched")
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")

    def create_suppliers_table(self):
        """Create suppliers table"""
        table_frame = tk.Frame(self.content_frame, bg="#cef5cb")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("Supplier ID", "First Name", "Last Name", "Date of Birth", "Address", "Phone", "Email")

        self.suppliers_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # Apply style for black header text
        style = ttk.Style()
        style.theme_use("clam")  # Use a theme that allows styling
        style.configure("Treeview.Heading", background="#7ecf78",foreground="black", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)

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

    def refresh_suppliers(self):
        """Refresh suppliers table"""
        try:
            if hasattr(self, 'suppliers_tree') and self.suppliers_tree:
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
        if not hasattr(self, 'suppliers_tree') or not self.suppliers_tree:
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
        if not hasattr(self, 'suppliers_tree') or not self.suppliers_tree:
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