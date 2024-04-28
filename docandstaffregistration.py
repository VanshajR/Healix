import customtkinter as cust
from CTkMessagebox import CTkMessagebox
import psycopg2
import os
import urllib.parse as up
from dotenv import load_dotenv
from tkcalendar import DateEntry

cust.set_appearance_mode("light")
cust.set_default_color_theme("green")


class StaffRegistrationWindow(cust.CTk):
    def __init__(self, title, width, height):
        super().__init__()

        # Initialize role attribute
        self.role = None

        # Set the window title and size
        self.title(title)
        self.geometry(f"{width}x{height}")

        # Create a canvas for scrollable area
        self.canvas = cust.CTkCanvas(self)
        self.canvas.pack(side=cust.LEFT, fill=cust.BOTH, expand=True)

        # Add a scrollbar to the canvas
        self.scrollbar = cust.CTkScrollbar(self, orientation=cust.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=cust.RIGHT, fill=cust.Y)

        # Configure the canvas to use the scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Create a frame inside the canvas to contain widgets
        self.frame = cust.CTkFrame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor=cust.NW)

        # Create the widgets for staff registration
        self.create_widgets()

    def create_widgets(self):
        # Create a title label
        self.label_title = cust.CTkLabel(self.frame, text="Staff Registration", font=("", 16))
        self.label_title.pack(pady=10)

        # Create buttons for selecting the role
        self.button_frame = cust.CTkFrame(self.frame)
        self.button_frame.pack(pady=10)

        self.doctor_button = cust.CTkButton(self.button_frame, text="Doctor", command=self.set_doctor_role)
        self.doctor_button.pack(side=cust.LEFT, padx=20)

        self.other_staff_button = cust.CTkButton(self.button_frame, text="Other Staff",
                                                 command=self.set_other_staff_role)
        self.other_staff_button.pack(side=cust.RIGHT, padx=20)

        # Create entry fields for staff information
        self.label_name = cust.CTkLabel(self.frame, text="Name:")
        self.label_name.pack(pady=5)
        self.entry_name = cust.CTkEntry(self.frame, width=300)
        self.entry_name.pack(pady=5)

        self.label_age = cust.CTkLabel(self.frame, text="Age:")
        self.label_age.pack(pady=5)
        self.entry_age = cust.CTkEntry(self.frame, width=300)
        self.entry_age.pack(pady=5)

        self.label_gender = cust.CTkLabel(self.frame, text="Gender (M/F/O):")
        self.label_gender.pack(pady=5)
        self.entry_gender = cust.CTkEntry(self.frame, width=300)
        self.entry_gender.pack(pady=5)

        self.label_address = cust.CTkLabel(self.frame, text="Address:")
        self.label_address.pack(pady=5)
        self.entry_address = cust.CTkEntry(self.frame, width=300)
        self.entry_address.pack(pady=5)

        self.label_department = cust.CTkLabel(self.frame, text="Department:")
        self.label_department.pack(pady=5)
        self.entry_department = cust.CTkEntry(self.frame, width=300)
        self.entry_department.pack(pady=5)

        self.label_salary = cust.CTkLabel(self.frame, text="Salary:")
        self.label_salary.pack(pady=5)
        self.entry_salary = cust.CTkEntry(self.frame, width=300)
        self.entry_salary.pack(pady=5)

        self.label_date_joining = cust.CTkLabel(self.frame, text="Date of Joining:")
        self.label_date_joining.pack(pady=5)
        self.date_joining = DateEntry(self.frame, date_pattern='yyyy-mm-dd', width=12)
        self.date_joining.pack(pady=5)

        # Additional entry fields for phone numbers
        self.label_phone_no1 = cust.CTkLabel(self.frame, text="Phone Number 1:")
        self.label_phone_no1.pack(pady=5)
        self.entry_phone_no1 = cust.CTkEntry(self.frame, width=300)
        self.entry_phone_no1.pack(pady=5)

        self.label_phone_no2 = cust.CTkLabel(self.frame, text="Phone Number 2:")
        self.label_phone_no2.pack(pady=5)
        self.entry_phone_no2 = cust.CTkEntry(self.frame, width=300)
        self.entry_phone_no2.pack(pady=5)

        # Entry field for password (only for doctor role)
        self.label_password = cust.CTkLabel(self.frame, text="Password:")
        self.entry_password = cust.CTkEntry(self.frame, show="*", width=300)
        self.label_password.pack_forget()
        self.entry_password.pack_forget()

        # Buttons for registering and clearing fields
        self.bottom_frame = cust.CTkFrame(self.frame)
        self.bottom_frame.pack(side=cust.BOTTOM, pady=10)

        self.register_button = cust.CTkButton(self.bottom_frame, text="Register", command=self.register_staff)
        self.register_button.pack(side=cust.LEFT, padx=10)

        self.clear_button = cust.CTkButton(self.bottom_frame, text="Clear", command=self.clear_fields)
        self.clear_button.pack(side=cust.RIGHT, padx=10)

    def set_doctor_role(self):
        self.role = "Doctor"
        self.label_password.pack(pady=5)
        self.entry_password.pack(pady=5)

    def set_other_staff_role(self):
        self.role = "Other Staff"
        self.label_password.pack_forget()
        self.entry_password.pack_forget()

    def register_staff(self):
        global conn, cursor
        name = self.entry_name.get()
        age = self.entry_age.get()
        gender = self.entry_gender.get().upper()
        address = self.entry_address.get()
        department = self.entry_department.get()
        salary = float(self.entry_salary.get())
        date_of_joining = self.date_joining.get_date()
        phone_no1 = self.entry_phone_no1.get() or None
        phone_no2 = self.entry_phone_no2.get() or None
        password = self.entry_password.get() if self.role == "Doctor" else None
        try:
            age = int(age)
            if age <= 0:
                CTkMessagebox(title="Invalid Age", message="Age must be a positive integer.", icon="warning")
                return
        except ValueError:
            CTkMessagebox(title="Invalid Age", message="Age must be a valid integer.", icon="warning")
            return

        # Check gender validity
        if gender not in ('M', 'F', 'O'):
            CTkMessagebox(title="Invalid Input", message="Gender must be 'M', 'F', or 'O'.", icon="warning")
            return

            # Check phone number validity
        if (phone_no1 and (not phone_no1.isdigit() or len(phone_no1) != 10)) or \
                (phone_no2 and (not phone_no2.isdigit() or len(phone_no2) != 10)):
            CTkMessagebox(title="Invalid Input", message="Phone number must be exactly 10 digits long.", icon="warning")
            return

            # Check for empty fields
        if not name:
            CTkMessagebox(title="Error", message="Name cannot be empty.", icon="warning")
            return

        if not address:
            CTkMessagebox(title="Error", message="Address cannot be empty.", icon="warning")
            return
        if self.role == "Doctor":
            if not password or len(password) < 8:
                CTkMessagebox(title="Error", message="Password must be at least 8 characters long.", icon="warning")
                return

        if not date_of_joining:
            CTkMessagebox(title="Error", message="Admission date cannot be empty.", icon="warning")
            return

        try:
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
            cursor = conn.cursor()

            # Execute the PL/SQL function to register the staff or doctor
            if self.role == "Doctor":
                cursor.execute("""
                    SELECT register_doctor(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (name, age, gender, address, department, salary, date_of_joining, phone_no1, phone_no2, password))
                result = cursor.fetchone()
                doctor_id = result[0]
                cursor.execute("""SELECT S_ID FROM Doctors WHERE Doc_ID=%s""",(doctor_id,))
                getstaffid = cursor.fetchone()
                staffid=getstaffid[0]
                CTkMessagebox(message=f"Registration successful!\nDoctor ID: {doctor_id} , Staff ID: {staffid}", icon="check")
            elif self.role == "Other Staff":
                cursor.execute("""
                    SELECT register_staff(%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (name, age, gender, address, department, salary, date_of_joining, phone_no1, phone_no2))
                result = cursor.fetchone()
                staff_id = result[0]
                CTkMessagebox(message=f"Registration successful!\nStaff ID: {staff_id}", icon="check")

            # Commit the transaction
            conn.commit()

        except Exception as e:
            # Roll back the transaction in case of an error
            conn.rollback()
            CTkMessagebox(title="Error", message=f"An error occurred: {e}", icon="cancel")

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def clear_fields(self):
        # Clear all entry fields
        self.entry_name.delete(0, cust.END)
        self.entry_age.delete(0, cust.END)
        self.entry_gender.delete(0, cust.END)
        self.entry_address.delete(0, cust.END)
        self.entry_department.delete(0, cust.END)
        self.entry_salary.delete(0, cust.END)
        self.entry_phone_no1.delete(0, cust.END)
        self.entry_phone_no2.delete(0, cust.END)

        # Clear the password field if it is visible
        if self.entry_password.winfo_ismapped():
            self.entry_password.delete(0, cust.END)
            self.label_password.pack_forget()
            self.entry_password.pack_forget()


# Example usage
if __name__ == "__main__":
    staff_registration_window = StaffRegistrationWindow("Staff Registration", 375, 900)
    staff_registration_window.resizable(width=False, height=True)

    staff_registration_window.mainloop()
