from assigndoctor import AssignmentWindow
from patientregistration import PatientRegistrationWindow
from docandstaffregistration import StaffRegistrationWindow
from viewdetails import DataRetrievalWindow
from updatedetails import UpdateWindow
from deletedata import DeleteWindow
from assigndoctor import AssignmentWindow
from viewassignments import AssignmentViewWindow
import customtkinter as cust
from CTkMessagebox import CTkMessagebox
import psycopg2
import os
import urllib.parse as up
from dotenv import load_dotenv
from tkcalendar import DateEntry
cust.set_appearance_mode("light")
cust.set_default_color_theme("green")
class AdminWindow(cust.CTk):
    def __init__(self, title, width, height):
        super().__init__()

        # Initialize the main window
        self.title(title)
        self.geometry(f"{width}x{height}")

        # Create buttons for various admin actions
        self.register_patient_button = cust.CTkButton(
            self, text="Patient Registration", command=self.open_patient_registration
        )
        self.register_patient_button.pack(pady=10)

        self.register_doctor_staff_button = cust.CTkButton(
            self, text="Doctor/Staff Registration", command=self.open_doctor_staff_registration
        )
        self.register_doctor_staff_button.pack(pady=10)

        self.view_records_button = cust.CTkButton(
            self, text="View Records", command=self.open_view_records
        )
        self.view_records_button.pack(pady=10)

        self.update_records_button = cust.CTkButton(
            self, text="Update Records", command=self.open_update_records
        )
        self.update_records_button.pack(pady=10)

        self.delete_records_button = cust.CTkButton(
            self, text="Delete Records", command=self.open_delete_records
        )
        self.delete_records_button.pack(pady=10)

        self.assign_doctor_button = cust.CTkButton(
            self, text="Assign Doctors", command=self.open_assign_doctor
        )
        self.assign_doctor_button.pack(pady=10)

        self.view_assignments_button = cust.CTkButton(
            self, text="View Assignments", command=self.open_view_assignments
        )
        self.view_assignments_button.pack(pady=10)

    def open_patient_registration(self):
        # Open the patient registration window
        registration_window = PatientRegistrationWindow("Patient Registration", 500, 750)
        # Start the main loop
        registration_window.resizable(width=False, height=False)
        registration_window.mainloop()

    def open_doctor_staff_registration(self):
        # Open the doctor/staff registration window
        staff_registration_window = StaffRegistrationWindow("Staff Registration", 375, 900)
        staff_registration_window.resizable(width=False, height=True)
        staff_registration_window.mainloop()

    def open_view_records(self):
        # Open the view records window
        data_retrieval_window = DataRetrievalWindow("Data Retrieval", 500, 300)
        data_retrieval_window.resizable(width=False, height=False)
        data_retrieval_window.mainloop()

    def open_update_records(self):
        # Open the update records window
        update_window = UpdateWindow("Data Update", 500, 200)
        update_window.resizable(width=False, height=False)
        update_window.mainloop()

    def open_delete_records(self):
        # Open the delete records window
        delete_window = DeleteWindow("Record Deletion", 600, 100)
        delete_window.resizable(width=False, height=False)
        delete_window.mainloop()

    def open_assign_doctor(self):
        assign_window = AssignmentWindow("Assignment", 500, 200)
        assign_window.resizable(width=False, height=False)
        assign_window.mainloop()
    def open_view_assignments(self):
        #Open the view assignments window
        assignment_window = AssignmentViewWindow("Assignment", 700, 300)
        assignment_window.resizable(width=False, height=False)
        assignment_window.mainloop()


if __name__ == "__main__":
    login_window = AdminWindow("Login", 300, 350)
    login_window.resizable(width=False, height=False)
    login_window.mainloop()
