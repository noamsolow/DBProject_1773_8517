# improved_main_application.py - Refactored Main GUI Application
import tkinter as tk
from tkinter import ttk, messagebox
import traceback
from datetime import datetime

# Import our real modules
from app.database import db_manager

# Import screen modules
from screens.dashboard_screen import DashboardScreen
from screens.workers_screen import WorkersScreen
from screens.suppliers_screen import SuppliersScreen
from screens.equipment_screen import EquipmentScreen
from screens.relationships_screen import RelationshipsScreen
from screens.reports_screen import ReportsScreen


class SportsInstituteApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gym Management System")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f8f9fa")

        # Set window icon and properties
        self.root.resizable(True, True)
        self.root.minsize(1000, 600)

        # Connect to database
        if not self.connect_database():
            return

        # Setup styles
        self.setup_styles()

        # Create main interface (but don't show welcome screen yet)
        self.create_main_interface_structure()

        # Initialize screen classes after the content frame is created
        self.dashboard_screen = DashboardScreen(self)
        self.workers_screen = WorkersScreen(self)
        self.suppliers_screen = SuppliersScreen(self)
        self.equipment_screen = EquipmentScreen(self)
        self.relationships_screen = RelationshipsScreen(self)
        self.reports_screen = ReportsScreen(self)

        # Now show the welcome screen
        self.show_welcome_screen()

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

    def create_main_interface_structure(self):
        """Create the main application interface structure"""
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

    def create_header(self, parent):
        """Create application header"""
        header_frame = tk.Frame(parent, bg="#36373d", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        # Title
        title_label = tk.Label(header_frame,
                               text="Gym Management System",
                               font=("Arial", 20, "bold"),
                               fg="white", bg="#36373d")
        title_label.pack(side="left", padx=20, pady=20)

        # Current time
        self.time_label = tk.Label(header_frame,
                                   text="",
                                   font=("Arial", 10),
                                   fg="#ecf0f1", bg="#36373d")
        self.time_label.pack(side="right", padx=20, pady=20)

        # Update time
        self.update_time()

    def create_sidebar(self, parent):
        """Create navigation sidebar"""
        sidebar_frame = tk.Frame(parent, bg="#545557", width=250)
        sidebar_frame.pack(side="left", fill="y")
        sidebar_frame.pack_propagate(False)

        # Navigation buttons
        nav_buttons = [
            ("🏠 Home", self.show_welcome_screen, "#3b404f"),
            ("👥 Workers", self.show_workers_screen, "#2a84ad"),
            ("🏭 Suppliers", self.show_suppliers_screen, "#48a843"),
            ("⚙️ Equipment", self.show_equipment_screen, "#cf3434"),
            ("🔗 Supplier Equipment", self.show_relationships_screen, "#e89820"),
            ("📊 Reports", self.show_reports_screen, "#841cad"),
            ("❌ Exit", self.exit_application, "#a8a6a3")
        ]

        # Add some spacing at top
        tk.Label(sidebar_frame, text="", bg="#545557", height=2).pack()

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

    # Screen navigation methods - delegate to respective screen classes
    def show_welcome_screen(self):
        """Show welcome/dashboard screen"""
        self.dashboard_screen.show_welcome_screen()

    def show_workers_screen(self):
        """Show workers management screen"""
        self.workers_screen.show_workers_screen()

    def show_suppliers_screen(self):
        """Show suppliers management screen"""
        self.suppliers_screen.show_suppliers_screen()

    def show_equipment_screen(self):
        """Show equipment management screen"""
        self.equipment_screen.show_equipment_screen()

    def show_relationships_screen(self):
        """Show equipment-supplier relationships screen"""
        self.relationships_screen.show_relationships_screen()

    def show_reports_screen(self):
        """Show reports and analytics screen"""
        self.reports_screen.show_reports_screen()

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