import tkinter as tk
from datetime import datetime
from app.database import db_manager


class DashboardScreen:
    def __init__(self, app):
        self.app = app
        self.root = app.root
        self.content_frame = app.content_frame
        self.update_status = app.update_status

    def show_welcome_screen(self):
        self.app.clear_content()
        self.content_frame.configure(bg="#d6d6d6")

        # Title
        title_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        title_frame.pack(fill="x", padx=30, pady=(20, 5))

        tk.Label(
            title_frame, text="🏋️ Gym Management Dashboard",
            font=("Arial", 26, "bold"), fg="#2b2b2b", bg="#f0f0f0"
        ).pack(anchor="w")

        now = datetime.now().strftime("%A, %d %B %Y | %H:%M")
        tk.Label(
            title_frame, text=f"📅 {now}",
            font=("Arial", 12), fg="#2b2b2b", bg="#f0f0f0"
        ).pack(anchor="w")

        # Dashboard Cards Grid
        cards_container = tk.Frame(self.content_frame, bg="#f0f0f0")
        cards_container.pack(fill="both", expand=True, padx=30, pady=10)

        stats = self.get_dashboard_stats()
        cards = [
            ("Total Workers", stats['workers'], "#3498db", "👥"),
            ("Total Suppliers", stats['suppliers'], "#1dbf22", "🏭"),
            ("Total Equipment", stats['equipment'], "#e74c3c", "⚙️"),
            ("Supplied Relations", stats['relationships'], "#f39c12", "🔗")
        ]

        for i, (title, count, color, icon) in enumerate(cards):
            self.create_card(cards_container, title, count, color, icon, row=i // 2, col=i % 2)

        # Quick Actions
        self.create_quick_actions()

        self.update_status("Dashboard loaded")

    def create_card(self, parent, title, count, color, icon, row, col):
        card = tk.Frame(parent, bg="#ffffff", bd=1, relief="solid")
        card.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)

        side_color = tk.Frame(card, bg=color, width=10)
        side_color.pack(side="left", fill="y")

        inner = tk.Frame(card, bg="#ffffff", padx=20, pady=10)
        inner.pack(fill="both", expand=True)

        tk.Label(inner, text=icon, font=("Arial", 30), fg=color, bg="#ffffff").pack(anchor="w")
        tk.Label(inner, text=str(count), font=("Arial", 26, "bold"), fg="#2b2b2b", bg="#ffffff").pack(anchor="w", pady=(5, 0))
        tk.Label(inner, text=title, font=("Arial", 13), fg="#454545", bg="#ffffff").pack(anchor="w")

    def create_quick_actions(self):
        frame = tk.Frame(self.content_frame, bg="#ecf0f1")
        frame.pack(fill="x", padx=30, pady=(10, 30))

        label = tk.Label(frame, text="🚀 Quick Actions", font=("Arial", 18, "bold"),
                         fg="#2b2b2b", bg="#ecf0f1")
        label.pack(anchor="w", pady=(0, 10))

        btn_frame = tk.Frame(frame, bg="#ecf0f1")
        btn_frame.pack(fill="x")

        buttons = [
            ("➕ Add New Worker", self.app.workers_screen.add_worker, "#4278ff"),
            ("🛠 Add New Equipment", self.app.equipment_screen.add_equipment, "#ff403b"),
            ("📈 View Reports", self.app.reports_screen.show_reports_screen, "#d43bff"),
            ("🔧 Manage Supplied Equipment", self.app.relationships_screen.show_relationships_screen, "#edaa2d")
        ]

        for i, (text, command, color) in enumerate(buttons):
            btn = tk.Button(
                btn_frame, text=text, command=command,
                font=("Arial", 11, "bold"), bg=color, fg="white",
                relief="flat", cursor="hand2", padx=15, pady=10, width=25
            )
            btn.grid(row=0, column=i, padx=10)
            btn_frame.grid_columnconfigure(i, weight=1)

    def get_dashboard_stats(self):
        stats = {'workers': 0, 'suppliers': 0, 'equipment': 0, 'relationships': 0}
        try:
            stats['workers'] = db_manager.execute_query("SELECT COUNT(*) FROM worker", fetch='one')[0]
            stats['suppliers'] = db_manager.execute_query("SELECT COUNT(*) FROM supplier", fetch='one')[0]
            stats['equipment'] = db_manager.execute_query("SELECT COUNT(*) FROM equipment", fetch='one')[0]
            stats['relationships'] = db_manager.execute_query("SELECT COUNT(*) FROM equipment_supplier", fetch='one')[0]
        except Exception as e:
            print(f"Error getting stats: {e}")
        return stats
