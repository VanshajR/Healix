import customtkinter as cust
from CTkMessagebox import CTkMessagebox
import psycopg2
import os
import urllib.parse as up
from dotenv import load_dotenv

# Set appearance and theme for the customtkinter window
cust.set_appearance_mode("light")
cust.set_default_color_theme("green")

# Define a named tuple for the details_record type returned by the function
from collections import namedtuple

DetailsRecord = namedtuple('DetailsRecord', [
    'id',
    'name',
    'age',
    'gender',
    'address',
    'department',
    'salary',
    'admission_date',
    'release_date',
    'date_of_joining',
    'phone_no',
    'password'
])


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


class DeleteWindow(cust.CTk):
    def __init__(self, title, width, height):
        super().__init__()

        # Initialize the main window
        self.title(title)
        self.geometry(f"{width}x{height}")

        # Create a frame for the options and inputs
        self.options_frame = cust.CTkFrame(self)
        self.options_frame.pack(pady=20)

        # Drop-down menu to select the category to delete
        self.delete_category = cust.CTkOptionMenu(
            self.options_frame, values=["Patient", "Doctor", "Staff"]
        )
        self.delete_category.pack(side=cust.LEFT, padx=10)
        self.delete_category.set("Patient")  # Default to "Patient"

        # Entry field for the ID to delete
        self.entry_id = cust.CTkEntry(self.options_frame, placeholder_text="Enter ID")
        self.entry_id.pack(side=cust.LEFT, padx=10)

        # Button to load data
        self.load_button = cust.CTkButton(
            self.options_frame, text="Load Data", command=self.load_data
        )
        self.load_button.pack(side=cust.LEFT, padx=10)

        # Button to delete the record
        self.delete_button = cust.CTkButton(
            self.options_frame, text="Delete", command=self.delete_record
        )
        self.delete_button.pack(side=cust.LEFT, padx=10)

        # Frame to display data
        self.data_frame = cust.CTkFrame(self)
        self.data_frame.pack(pady=20)
        self.data_frame.pack_forget()

        # Create dictionaries to hold labels
        self.labels = {}

    def load_data(self):
        # Clear existing labels
        for widget in self.data_frame.winfo_children():
            widget.destroy()

        # Get the category and ID from the GUI
        category = self.delete_category.get()
        id_to_delete = self.entry_id.get()

        # Connect to the database
        conn = connect_to_database()
        cursor = conn.cursor()

        try:
            # Call the function fetch_details in PostgreSQL
            cursor.callproc('fetch_details', (category, int(id_to_delete)))

            # Fetch the result and create a DetailsRecord from it
            result = cursor.fetchone()
            if result:
                record = DetailsRecord(*result)

                # Define attributes based on the category
                if category == 'Patient':
                    attributes = [
                        'id', 'name', 'age', 'gender',
                        'address', 'phone_no', 'password',
                        'admission_date', 'release_date'
                    ]
                elif category == 'Doctor':
                    attributes = [
                        'id', 'name', 'age', 'gender',
                        'address', 'department', 'salary', 'date_of_joining'
                    ]
                elif category == 'Staff':
                    attributes = [
                        'id', 'name', 'age', 'gender',
                        'address', 'department', 'salary', 'date_of_joining'
                    ]

                # Create labels for each attribute
                self.labels.clear()
                for i, attribute in enumerate(attributes):
                    label = cust.CTkLabel(self.data_frame, text=f"{attribute}: {getattr(record, attribute)}")
                    label.grid(row=i, column=0, padx=5, pady=5, sticky='w')
                    self.labels[attribute] = label
                # Calculate the new height of the window based on the number of attributes
                new_height = 100 + len(attributes) *40  # Adjust this value as needed

                # Set the new height for the window
                self.geometry(f"{self.winfo_width()}x{new_height}")
                self.data_frame.pack()
                self.resizable(width=False, height=False)

            else:
                CTkMessagebox(title="No Results", message="No results found for the provided ID.", icon="warning")
            self.data_loaded = True
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}", icon="cancel")
            print(f"An error occurred: {e}")

        finally:
            cursor.close()
            conn.close()

    def delete_record(self):
        # Get the category and ID from the GUI
        category = self.delete_category.get()
        id_to_delete = self.entry_id.get()

        # Connect to the database
        conn = connect_to_database()
        cursor = conn.cursor()

        try:
            if category == "Patient":
                # Call the PL/SQL procedure delete_patient using cursor.execute() with CALL
                cursor.execute("CALL delete_patient(%s)", (int(id_to_delete),))
            elif category == "Doctor":
                # Call the PL/SQL procedure delete_doctor using cursor.execute() with CALL
                cursor.execute("CALL delete_doctor(%s)", (int(id_to_delete),))
            elif category == "Staff":
                # Check if staff member is also a doctor (assuming Staff_ID is a foreign key in Doctors)
                cursor.execute(
                    "SELECT EXISTS(SELECT 1 FROM Doctors WHERE S_ID = %s)", (int(id_to_delete),)
                )
                is_doctor = cursor.fetchone()[0]  # Check if query returned True

                # Delete from Staff first
                cursor.execute("CALL delete_staff(%s)", (int(id_to_delete),))

                # If doctor, delete from Doctors as well (cascading deletes won't handle this)
                if is_doctor:
                    cursor.execute("SELECT Doc_ID FROM Doctors WHERE S_ID=%s", (int(id_to_delete),))
                    doctor_record = cursor.fetchone()  # Fetch doctor record (might be None)
                    if doctor_record:
                        doctor_id = doctor_record[0]
                        cursor.execute("CALL delete_doctor(%s)", (int(doctor_id),))
                    else:
                        print("Staff member not found in Doctors table (might already be deleted).")

            # Commit the transaction
            conn.commit()
            CTkMessagebox(title="Success", message="Record deleted successfully!", icon="check")

        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}", icon="cancel")
            print(f"An error occurred: {e}")

        finally:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    delete_window = DeleteWindow("Record Deletion", 600, 100)
    delete_window.mainloop()
