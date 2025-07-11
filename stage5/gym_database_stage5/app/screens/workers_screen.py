# screens/workers_screen.py
import tkinter as tk
from tkinter import ttk, messagebox
from app.operations.worker_operations import WorkerOperations, WorkerDialog


class WorkersScreen:
    def __init__(self, app):
        self.app = app
        self.root = app.root
        self.content_frame = app.content_frame
        self.update_status = app.update_status
        self.worker_ops = WorkerOperations()
        self.worker_search_var = None
        self.workers_tree = None

    def show_workers_screen(self):
        """Show workers management screen"""
        self.app.clear_content()
        self.content_frame.configure(bg="#edeffc")


        # Header
        header_frame = tk.Frame(self.content_frame, bg="#d6e5ff")
        header_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(header_frame, text="Worker Management",
                 font=("Arial", 18, "bold"), fg="#011233", bg="#d6e5ff").pack(side="left")

        # Search bar
        search_frame = tk.Frame(self.content_frame, bg="#d6e5ff")
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="Search:", font=("Arial", 11), bg="#d6e5ff").pack(side="left")
        self.worker_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.worker_search_var, width=30, font=("Arial", 10))
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", lambda e: self.search_workers())

        tk.Button(search_frame, text="Clear", command=self.refresh_workers,
                  font=("Arial", 10), bg="#878b9c", fg="white").pack(side="left", padx=5)

        # Control buttons
        btn_frame = tk.Frame(header_frame, bg="#d3d8ed")
        btn_frame.pack(side="right")

        buttons = [
            ("Add Worker", self.add_worker, "#121c45"),
            ("Edit Worker", self.edit_worker, "#20317a"),
            ("Delete Worker", self.delete_worker, "#2d44a6"),
            ("Refresh", self.refresh_workers, "#3b58d4")
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
        table_frame = tk.Frame(self.content_frame, bg="#d6e5ff")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Apply style for black header text
        style = ttk.Style()
        style.theme_use("clam")  # Use a theme that allows styling
        style.configure("Treeview.Heading", background="#a0b1f2",foreground="black", font=("Segoe UI", 10, "bold"))
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
                   query_text in str(worker[1]).lower() or  # first name
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

    def refresh_workers(self):
        """Refresh workers table"""
        try:
            if hasattr(self, 'workers_tree') and self.workers_tree:
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
        if not hasattr(self, 'workers_tree') or not self.workers_tree:
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
        if not hasattr(self, 'workers_tree') or not self.workers_tree:
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