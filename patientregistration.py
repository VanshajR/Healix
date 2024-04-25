# Adjust the import statement to include the new table name
from tkcalendar import DateEntry
import customtkinter as cust
from CTkMessagebox import CTkMessagebox
import psycopg2
import os
import urllib.parse as up
from dotenv import load_dotenv

cust.set_appearance_mode("light")
cust.set_default_color_theme("green")


class PatientRegistrationWindow(cust.CTk):
    def __init__(self, title, width, height):
        super().__init__()

        # Set the window title and size
        self.title(title)
        self.geometry(f"{width}x{height}")

        # Create the label and entry for each required field
        self.create_widgets()

        # Set a small delay to ensure the window is initialized
        self.after(100, self.show_calendar)

    def create_widgets(self):
        self.label_name = cust.CTkLabel(self, text="Name:")
        self.label_name.pack(pady=5)
        self.entry_name = cust.CTkEntry(self, width=300)
        self.entry_name.pack(pady=5)

        self.label_age = cust.CTkLabel(self, text="Age:")
        self.label_age.pack(pady=5)
        self.entry_age = cust.CTkEntry(self, width=300)
        self.entry_age.pack(pady=5)

        self.label_gender = cust.CTkLabel(self, text="Gender:")
        self.label_gender.pack(pady=5)
        self.entry_gender = cust.CTkEntry(self, width=300)
        self.entry_gender.pack(pady=5)

        self.label_address = cust.CTkLabel(self, text="Address:")
        self.label_address.pack(pady=5)
        self.entry_address = cust.CTkEntry(self, width=300)
        self.entry_address.pack(pady=5)

        self.label_phone_no1 = cust.CTkLabel(self, text="Phone Number 1:")
        self.label_phone_no1.pack(pady=5)
        self.entry_phone_no1 = cust.CTkEntry(self, width=300)
        self.entry_phone_no1.pack(pady=5)

        self.label_phone_no2 = cust.CTkLabel(self, text="Phone Number 2:")
        self.label_phone_no2.pack(pady=5)
        self.entry_phone_no2 = cust.CTkEntry(self, width=300)
        self.entry_phone_no2.pack(pady=5)

        self.label_password = cust.CTkLabel(self, text="Password:")
        self.label_password.pack(pady=5)
        self.entry_password = cust.CTkEntry(self, show="*", width=300)
        self.entry_password.pack(pady=5)

        font_style = cust.CTkFont(family="Helvetica", size=16, weight="normal")

        self.label_admission_date = cust.CTkLabel(self, text="Admission Date:")
        self.label_admission_date.pack(pady=5)
        self.date_admission_date = DateEntry(self, width=15, date_pattern='yyyy-mm-dd')
        self.date_admission_date['font'] = font_style  # Apply the custom font style
        self.date_admission_date.pack(pady=5)

        # Register button
        self.register_button = cust.CTkButton(self, text="Register", command=self.register_patient)
        self.register_button.pack(pady=20)

        # Clear button
        self.clear_button = cust.CTkButton(self, text="Clear", command=self.clear_fields)
        self.clear_button.pack(pady=20)

    def show_calendar(self):
        # Focus on the DateEntry widget and trigger the calendar dropdown
        self.date_admission_date.focus_set()
        # Simulate a down arrow key press to expand the calendar dropdown
        self.date_admission_date.event_generate('<Down>')

    def clear_fields(self):
        # Clear all entry fields
        self.entry_name.delete(0, cust.END)
        self.entry_age.delete(0, cust.END)
        self.entry_gender.delete(0, cust.END)
        self.entry_address.delete(0, cust.END)
        self.entry_phone_no1.delete(0, cust.END)
        self.entry_phone_no2.delete(0, cust.END)
        self.entry_password.delete(0, cust.END)

        current_date = self.date_admission_date.get_date()  # Retrieve the current date
        self.date_admission_date.set_date(current_date)  # Set the date to the current date

        self.date_admission_date.update_idletasks()
        self.entry_name.focus_set()
        self.date_admission_date.focus_set()

    def register_patient(self):
        name = self.entry_name.get()
        age = self.entry_age.get()
        gender = self.entry_gender.get().upper()
        address = self.entry_address.get()
        phone_no1 = self.entry_phone_no1.get() or None  # Treat empty entry as NULL
        phone_no2 = self.entry_phone_no2.get() or None  # Treat empty entry as NULL
        password = self.entry_password.get()
        admission_date = self.date_admission_date.get_date().strftime('%Y-%m-%d')

        # Perform input validation
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

        if not password or len(password) < 8:
            CTkMessagebox(title="Error", message="Password must be at least 8 characters long.", icon="warning")
            return

        if not admission_date:
            CTkMessagebox(title="Error", message="Admission date cannot be empty.", icon="warning")
            return

        # If input is valid, register the patient
        try:
            load_dotenv()
            DATABASE_URL = os.getenv("DATABASE_URL")

            url = up.urlparse(DATABASE_URL)
            with psycopg2.connect(
                    database=url.path[1:],
                    user=url.username,
                    password=url.password,
                    host=url.hostname,
                    port=url.port
            ) as conn:
                with conn.cursor() as cursor:
                    # Call the PL/pgSQL function to register the patient
                    cursor.execute(
                        "SELECT register_patient(%s, %s, %s, %s, %s, %s, %s, %s)",
                        (name, age, gender, address, phone_no1, phone_no2, password, admission_date)
                    )
                    patient_id = cursor.fetchone()[0]

                    # Commit the transaction
                    conn.commit()

                    # Display a success message with the patient ID
                    CTkMessagebox(message=f"Patient registered successfully!\nPatient ID: {patient_id}",
                                  icon="check", option_1="Thanks")

        except psycopg2.Error as db_error:
            # Roll back the transaction in case of a database error
            CTkMessagebox(title="Database Error", message=f"A database error occurred: {db_error}", icon="cancel")

        except Exception as e:
            # Display an error message for other exceptions
            CTkMessagebox(title="Error", message=f"An error occurred: {e}", icon="cancel")


# Example usage
if __name__ == "__main__":
    # Create the patient registration window
    registration_window = PatientRegistrationWindow("Patient Registration", 500, 700)
    # Start the main loop
    registration_window.mainloop()
