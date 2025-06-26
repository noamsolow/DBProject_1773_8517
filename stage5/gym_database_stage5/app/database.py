# database_config.py - Focused on Equipment, Workers, Suppliers, Equipment_Supplier
import psycopg2
from psycopg2 import Error
import tkinter.messagebox as messagebox


class DatabaseManager:
    def __init__(self):
        # PostgreSQL connection parameters
        self.db_params = {
            'host': 'localhost',
            'port': '5432',
            'database': 'intagratedDBs',
            'user': 'nsolow',
            'password': 'noam2004'
        }
        self.connection = None

    def connect(self):
        """Establish connection to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(**self.db_params)
            self.connection.autocommit = False
            print("Database connection successful!")
            return True
        except Error as e:
            error_msg = f"Database connection failed:\n{str(e)}\n\nPlease check your database credentials in database_config.py"
            print(error_msg)
            messagebox.showerror("Connection Error", error_msg)
            return False

    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("Database connection closed")

    def execute_query(self, query, params=None, fetch=False):
        """Execute a database query"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)

            if fetch:
                if fetch == 'one':
                    result = cursor.fetchone()
                elif fetch == 'all':
                    result = cursor.fetchall()
                else:
                    result = cursor.fetchmany(fetch)
                cursor.close()
                return result
            else:
                cursor.close()
                return True

        except Error as e:
            print(f"Database query error: {e}")
            self.connection.rollback()
            raise e

    def commit(self):
        """Commit current transaction"""
        try:
            self.connection.commit()
        except Error as e:
            print(f"Commit error: {e}")
            self.connection.rollback()
            raise e

    def rollback(self):
        """Rollback current transaction"""
        try:
            self.connection.rollback()
        except Error as e:
            print(f"Rollback error: {e}")
            raise e


# Global database manager instance
db_manager = DatabaseManager()