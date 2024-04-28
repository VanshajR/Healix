import customtkinter as cust
from CTkMessagebox import CTkMessagebox
import psycopg2
import os
import urllib.parse as up
from dotenv import load_dotenv
from tkinter import ttk

# Set appearance and theme for the customtkinter window
cust.set_appearance_mode("light")
cust.set_default_color_theme("green")


def connect_to_database():
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")

    url = up.urlparse(DATABASE_URL)
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    return conn


class AssignmentViewWindow(cust.CTk):
    def __init__(self, title, width, height):
        super().__init__()

        # Initialize the main window
        self.title(title)
        self.geometry(f"{width}x{height}")

        # Create a frame for the table
        self.table_frame = cust.CTkFrame(self)
        self.table_frame.pack(padx=20, pady=20)

        # Create the table
        self.table = ttk.Treeview(self.table_frame, columns=("Patient ID", "Patient Name", "Doctor ID", "Doctor Name"),
                                  show="headings")
        self.table.pack(fill="both", expand=True)

        # Setup table columns
        self.table.heading("Patient ID", text="Patient ID")
        self.table.heading("Patient Name", text="Patient Name")
        self.table.heading("Doctor ID", text="Doctor ID")
        self.table.heading("Doctor Name", text="Doctor Name")

        # Create the Delete button
        self.delete_button = cust.CTkButton(self, text="Delete", command=self.delete_record)
        self.delete_button.pack(pady=10)

        # Populate the table
        self.populate_table()

    def populate_table(self):
        conn = connect_to_database()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT a.patient_id, p.name AS patient_name, a.doc_id, s.name AS doctor_name
                FROM assignment a
                JOIN patients p ON a.patient_id = p.patient_id
                JOIN doctors d ON a.doc_id = d.doc_id
                JOIN staff s ON d.s_id = s.s_id
            """)
            records = cursor.fetchall()

            # Insert records into the table
            for record in records:
                self.table.insert("", "end", values=record)

        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}", icon="cancel")
            print(f"An error occurred: {e}")

        finally:
            cursor.close()
            conn.close()

    def delete_record(self):
        selected_items = self.table.selection()  # Get the list of selected items in the table
        if not selected_items:
            CTkMessagebox(title="No Selection", message="Please select one or more records to delete.", icon="warning")
            return

        conn = connect_to_database()
        cursor = conn.cursor()

        try:
            for item in selected_items:
                patient_id = self.table.item(item, "values")[0]  # Get the patient ID from the selected item
                cursor.execute("DELETE FROM assignment WHERE patient_id = %s", (patient_id,))
                self.table.delete(item)  # Delete the selected item from the table

            conn.commit()
            CTkMessagebox(title="Success", message="Records deleted successfully.", icon="info")

        except Exception as e:
            conn.rollback()
            CTkMessagebox(title="Error", message=f"An error occurred: {e}", icon="cancel")

        finally:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    assignment_view_window = AssignmentViewWindow("Assignment View", 600, 300)
    assignment_view_window.mainloop()
