# screens/equipment_screen.py
import tkinter as tk
from tkinter import ttk, messagebox
from app.operations.equipment_operations import EquipmentOperations, EquipmentDialog

class EquipmentScreen:
    def __init__(self, app):
        self.app = app
        self.root = app.root
        self.content_frame = app.content_frame
        self.update_status = app.update_status
        self.equipment_ops = EquipmentOperations()
        self.equipment_search_var = None
        self.equipment_tree = None

    def show_equipment_screen(self):
        """Show equipment management screen"""
        self.app.clear_content()
        self.content_frame.configure(bg="#ffebeb")


        # Header
        header_frame = tk.Frame(self.content_frame, bg="#ffd4d4")
        header_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(header_frame, text="Equipment Management",
                 font=("Arial", 18, "bold"), fg="#3d0307", bg="#ffd4d4").pack(side="left")

        # Control buttons
        btn_frame = tk.Frame(header_frame, bg="#ffd4d4")
        btn_frame.pack(side="right")

        # Add search bar under header
        search_frame = tk.Frame(self.content_frame, bg="#ffd4d4")
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="Search:", font=("Arial", 11), bg="#ffd4d4").pack(side="left")
        self.equipment_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.equipment_search_var, width=30, font=("Arial", 10))
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", lambda e: self.search_equipment())

        tk.Button(search_frame, text="Clear", command=self.refresh_equipment,
                  font=("Arial", 10), bg="#95a5a6", fg="white").pack(side="left", padx=5)

        buttons = [
            ("Add Equipment", self.add_equipment, "#69070d"),
            ("Edit Equipment", self.edit_equipment, "#b00c16"),
            ("Delete Equipment", self.delete_equipment, "#de0b17"),
            ("Refresh", self.refresh_equipment, "#ff2430")
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
        table_frame = tk.Frame(self.content_frame, bg="#ffd4d4")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("Equipment ID", "Name", "Category", "Purchase Date", "Warranty Expiry", "Brand")

        self.equipment_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        # Apply style for black header text
        style = ttk.Style()
        style.theme_use("clam")  # Use a theme that allows styling
        style.configure("Treeview.Heading", background="#f7747f", foreground="black", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)

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

    def refresh_equipment(self):
        """Refresh equipment table"""
        try:
            if hasattr(self, 'equipment_tree') and self.equipment_tree:
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
        if not hasattr(self, 'equipment_tree') or not self.equipment_tree:
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
        if not hasattr(self, 'equipment_tree') or not self.equipment_tree:
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