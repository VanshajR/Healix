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

class AssignmentWindow(cust.CTk):
    def __init__(self, title, width, height):
        super().__init__()

        # Initialize the main window
        self.title(title)
        self.geometry(f"{width}x{height}")

        # Create input frame
        self.input_frame = cust.CTkFrame(self)
        self.input_frame.pack(pady=20)

        # Labels and entries for department, patient_id, and doc_id
        self.label_department = cust.CTkLabel(self.input_frame, text="Department:")
        self.label_department.grid(row=0, column=0, padx=10, pady=5)
        self.entry_department = cust.CTkEntry(self.input_frame)
        self.entry_department.grid(row=0, column=1, padx=10, pady=5)

        self.label_patient_id = cust.CTkLabel(self.input_frame, text="Patient ID:")
        self.label_patient_id.grid(row=1, column=0, padx=10, pady=5)
        self.entry_patient_id = cust.CTkEntry(self.input_frame)
        self.entry_patient_id.grid(row=1, column=1, padx=10, pady=5)

        self.label_doc_id = cust.CTkLabel(self.input_frame, text="Doctor ID:")
        self.label_doc_id.grid(row=2, column=0, padx=10, pady=5)
        self.entry_doc_id = cust.CTkEntry(self.input_frame)
        self.entry_doc_id.grid(row=2, column=1, padx=10, pady=5)

        # Buttons to view doctors and assign doctor
        self.view_button = cust.CTkButton(
            self.input_frame, text="View Doctor Details", command=self.view_doctor_details
        )
        self.view_button.grid(row=3, column=0, padx=10, pady=10)

        self.assign_button = cust.CTkButton(
            self.input_frame, text="Assign Doctor", command=self.assign_doctor
        )
        self.assign_button.grid(row=3, column=1, padx=10, pady=10)

    def view_doctor_details(self):
        department = self.entry_department.get()

        conn = None
        cursor = None
        try:
            conn = connect_to_database()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT D.doc_id, S.name
                FROM Doctors D
                JOIN Staff S ON D.s_id = S.s_id
                WHERE S.department ILIKE %s
            """, (f"%{department}%",))

            results = cursor.fetchall()

            if results:
                self.display_doctor_table(results)
            else:
                CTkMessagebox(title="No Results", message="No doctors found for the given department.", icon="warning")

        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}", icon="cancel")
            print(f"An error occurred: {e}")

        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    def assign_doctor(self):
        department = self.entry_department.get()
        patient_id = self.entry_patient_id.get()
        doc_id = self.entry_doc_id.get()

        conn = None
        cursor = None
        try:
            conn = connect_to_database()
            cursor = conn.cursor()

            # Check if the assignment already exists
            cursor.execute("""
                SELECT 1 FROM assignment
                WHERE patient_id = %s AND doc_id = %s
            """, (patient_id, doc_id))

            if cursor.fetchone():
                CTkMessagebox(title="Assignment Exists", message="This assignment already exists.", icon="info")
            else:
                # Insert the assignment
                cursor.execute("""
                    CALL assign_doctor_to_patient(%s,%s)
                """, (patient_id, doc_id))

                conn.commit()

                CTkMessagebox(title="Assignment Successful", message="Doctor assigned to patient successfully.",
                               icon="info")

        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}", icon="cancel")
            print(f"An error occurred: {e}")

        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    def display_doctor_table(self, results):
        result_window = cust.CTkToplevel(self)
        result_window.title("Doctor Details")

        if results:
            table = ttk.Treeview(result_window, columns=("Doctor ID", "Name"), show="headings")
            table.pack(fill="both", expand=True)

            table.heading("Doctor ID", text="Doctor ID")
            table.heading("Name", text="Name")

            for result in results:
                table.insert("", cust.END, values=result)

if __name__ == "__main__":
    assignment_window = AssignmentWindow("Assignment Window", 400, 250)
    assignment_window.mainloop()
