# screens/relationships_screen.py
import tkinter as tk
from tkinter import ttk, messagebox
from app.operations.equipment_supplier_operations import EquipmentSupplierOperations, EquipmentSupplierDialog


class RelationshipsScreen:
    def __init__(self, app):
        self.app = app
        self.root = app.root
        self.content_frame = app.content_frame
        self.update_status = app.update_status
        self.es_ops = EquipmentSupplierOperations()
        self.relationship_search_var = None
        self.relationships_tree = None

    def show_relationships_screen(self):
        """Show equipment-supplier relationships screen"""
        self.app.clear_content()
        self.content_frame.configure(bg="#fffbeb")


        # Header
        header_frame = tk.Frame(self.content_frame, bg="#faf2bb")
        header_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(header_frame, text="Equipment-Supplier Relationships",
                 font=("Arial", 18, "bold"), fg="#4f3d02", bg="#faf2bb").pack(side="left")

        # Control buttons
        btn_frame = tk.Frame(header_frame, bg="#faf2bb")
        btn_frame.pack(side="right")

        # Add search bar under header
        search_frame = tk.Frame(self.content_frame, bg="#faf2bb")
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="Search:", font=("Arial", 11), bg="#faf2bb").pack(side="left")
        self.relationship_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.relationship_search_var, width=30, font=("Arial", 10))
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", lambda e: self.search_relationships())

        tk.Button(search_frame, text="Clear", command=self.refresh_relationships,
                  font=("Arial", 10), bg="#95a5a6", fg="white").pack(side="left", padx=5)

        buttons = [
            ("Add Relationship", self.add_relationship, "#694905"),
            ("Edit Relationship", self.edit_relationship, "#8c6208"),
            ("Delete Relationship", self.delete_relationship, "#b57f0d"),
            ("Refresh", self.refresh_relationships, "#e6a317")
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
        table_frame = tk.Frame(self.content_frame, bg="#faf2bb")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("Eq. ID", "Equipment", "Category", "Person ID", "Person Name", "Quantity", "Supply Date")

        self.relationships_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        # Apply style for black header text
        style = ttk.Style()
        style.theme_use("clam")  # Use a theme that allows styling
        style.configure("Treeview.Heading", background="#f2b638", foreground="black", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)

        # Configure columns
        widths = [60, 150, 100, 80, 150, 80, 100]
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
                if query in str(rel[0]).lower() or  # eq id
                   query in str(rel[1]).lower() or  # eq name
                   query in str(rel[2]).lower() or # category
                   query in str(rel[3]).lower() or  # person id
                   query in str(rel[4]).lower() or  # Person Name
                   query in str(rel[5]).lower() or  # quantity
                   query in str(rel[6]).lower()   # supply date
            ]
            self.relationships_tree.delete(*self.relationships_tree.get_children())
            for rel in filtered:
                self.relationships_tree.insert("", "end", values=rel)

            self.update_status(f"{len(filtered)} relationship(s) matched")
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")

    def refresh_relationships(self):
        """Refresh relationships table"""
        try:
            if hasattr(self, 'relationships_tree') and self.relationships_tree:
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
        if not hasattr(self, 'relationships_tree') or not self.relationships_tree:
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
        if not hasattr(self, 'relationships_tree') or not self.relationships_tree:
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