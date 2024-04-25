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
    'password',
    'phone_no1',
    'phone_no2'  # New field for the second phone number
], defaults=[None, None, None, None, None, None, None, None, None, None, None])


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


class UpdateWindow(cust.CTk):
    def __init__(self, title, width, height):
        super().__init__()

        # Initialize the main window
        self.title(title)
        self.geometry(f"{width}x{height}")

        # Create a frame for the options and inputs
        self.options_frame = cust.CTkFrame(self)
        self.options_frame.pack(pady=20)

        # Drop-down menu to select the category to update
        self.update_category = cust.CTkOptionMenu(
            self.options_frame, values=["Patient", "Doctor", "Staff"]
        )
        self.update_category.pack(side=cust.LEFT, padx=10)
        self.update_category.set("Patient")  # Default to "Patient"

        # Entry field for the ID to update
        self.entry_id = cust.CTkEntry(self.options_frame, placeholder_text="Enter ID")
        self.entry_id.pack(side=cust.LEFT, padx=10)

        # Button to load data
        self.load_button = cust.CTkButton(
            self.options_frame, text="Load Data", command=self.load_data
        )
        self.load_button.pack(side=cust.LEFT, padx=10)

        # Frame for the update button
        self.update_frame = cust.CTkFrame(self)
        self.update_frame.pack(pady=10)

        # Button to update the data
        self.update_button = cust.CTkButton(
            self.update_frame, text="Update", command=self.update_data
        )
        self.update_button.pack(pady=5)

        # Frame to display and edit data
        self.data_frame = cust.CTkFrame(self)
        # Initially, the data frame is hidden until data is loaded
        self.data_frame.pack(pady=20)
        self.data_frame.pack_forget()

        # Create dictionaries to hold entry fields and their labels
        self.entry_fields = {}
        self.labels = {}

    def load_data(self):
        # Clear existing entry fields and labels
        global attributes
        for widget in self.data_frame.winfo_children():
            widget.destroy()

        # Get the category and ID from the GUI
        category = self.update_category.get()
        id_to_update = self.entry_id.get()

        # Connect to the database
        conn = connect_to_database()
        cursor = conn.cursor()

        try:
            # Call the function fetch_details in PostgreSQL
            cursor.callproc('fetch_details', (category, int(id_to_update)))

            # Fetch the result and create a DetailsRecord from it
            result = cursor.fetchone()
            print(result)
            if result:
                record = DetailsRecord(*result)

                # Show the data frame
                self.data_frame.pack(pady=20)

                # Define attributes based on the category
                if category == 'Patient':
                    attributes = [
                        'id', 'name', 'age', 'gender',
                        'address', 'password', 'phone_no1', 'phone_no2',
                        'admission_date', 'release_date'
                    ]
                elif category == 'Doctor':
                    attributes = [
                        'id', 'name', 'age', 'gender',
                        'address', 'department', 'salary', 'date_of_joining', 'password',
                        'phone_no1', 'phone_no2'
                    ]
                elif category == 'Staff':
                    attributes = [
                        'id', 'name', 'age', 'gender',
                        'address', 'department', 'salary', 'date_of_joining',
                        'phone_no1', 'phone_no2'
                    ]

                # Create entry fields and labels for each attribute
                self.entry_fields.clear()
                for i, attribute in enumerate(attributes):
                    label = cust.CTkLabel(self.data_frame, text=attribute)
                    label.grid(row=i, column=0, padx=5, pady=5, sticky='e')
                    entry = cust.CTkEntry(self.data_frame)
                    entry.grid(row=i, column=1, padx=5, pady=5)

                    # Set the default text of the entry field to the current value of the attribute
                    entry.insert(0, str(getattr(record, attribute)))

                    # If updating release_date and the attribute is for a patient, set default entry to NULL
                    if category == 'Patient' and attribute == 'release_date':
                        entry.delete(0, cust.END)  # Clear the entry and set it to NULL

                    # Save the entry field and label
                    self.entry_fields[attribute] = entry
                    # Calculate the new height of the window based on the number of attributes
                    new_height = 100 + len(attributes) * 50  # Adjust this value as needed

                    # Set the new height for the window
                    self.geometry(f"600x{new_height}")
                    self.data_frame.pack()

            else:
                CTkMessagebox(title="No Results", message="No results found for the provided ID.", icon="warning")

        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}", icon="cancel")
            print(f"An error occurred: {e}")

        finally:
            cursor.close()
            conn.close()

    def update_data(self):
        # Get the category and ID from the GUI
        category = self.update_category.get()
        id_to_update = self.entry_id.get()

        # Gather the data to update
        updated_data = {}
        for attribute, entry in self.entry_fields.items():
            # Get the user input from each entry field
            entry_value = entry.get()

            # For release_date, set it to None if the field is empty (default to NULL)
            if attribute == 'release_date' and category == 'Patient':
                if entry_value.strip() == "":
                    entry_value = None  # Set release_date to NULL if the entry is empty
            if attribute == 'phone_no1' or attribute == 'phone_no2':
                if entry_value.strip() == "":  # Check if phone number field is empty
                    entry_value = None
            updated_data[attribute] = entry_value

        # Connect to the database
        conn = connect_to_database()
        cursor = conn.cursor()

        try:
            # Call the appropriate update procedure based on the category
            if category == "Patient":
                # Call the PL/SQL procedure update_patient using cursor.execute() with CALL
                cursor.execute(
                    "CALL update_patient(%s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        int(id_to_update),
                        updated_data['name'],
                        int(updated_data['age']),
                        updated_data['gender'],
                        updated_data['address'],
                        updated_data['password'],
                        updated_data['admission_date'],
                        updated_data['release_date']
                    )
                )
                cursor.execute(
                    "CALL update_patient_phone_numbers(%s, %s, %s)",
                    (
                        int(id_to_update),
                        updated_data.get('phone_no1'),  # Use value if present
                        updated_data.get('phone_no2')  # Use value if present
                    )
                )


            elif category == "Doctor":
                doctor_id = int(id_to_update)
                # Update staff information (assuming id_to_update references staff_id)
                cursor.execute(
                    "SELECT S_ID FROM Doctors WHERE Doc_ID = %s",
                    (doctor_id,)  # Use a tuple for single parameter
                )

                # Fetch the retrieved staff ID (if any)
                staff_id = cursor.fetchone()  # Returns a tuple or None

                if staff_id is None:
                    # Handle case where no doctor found with the ID
                    # (raise exception, display error message, etc.)
                    pass
                else:
                    # Extract the staff ID from the fetched tuple
                    staff_id = staff_id[0]  # Assuming Staff_ID is the first column

                cursor.execute(

                    "CALL update_staff(%s, %s, %s, %s, %s, %s, %s, %s)",

                    (

                        int(staff_id),

                        updated_data['name'],

                        int(updated_data['age']),

                        updated_data['gender'],

                        updated_data['address'],

                        updated_data['department'],

                        float(updated_data['salary']),

                        updated_data['date_of_joining']

                    )

                )

                # Update doctor password (assuming doc_id exists in updated_data)

                if 'Doc_ID' in updated_data and updated_data['pass']:  # Check for doc_id and password

                    cursor.execute(

                        "CALL update_doctor(%s, %s)",

                        (

                            int(id_to_update),

                            updated_data['pass']

                        )

                    )

                # Update doctor phone numbers (similar to staff)

                cursor.execute(

                    "CALL update_staff_phone_numbers(%s, %s, %s)",

                    (

                        int(staff_id),

                        updated_data.get('phone_no1'),  # Use value if present

                        updated_data.get('phone_no2')  # Use value if present

                    )

                )

            elif category == "Staff":
                # Call the PL/SQL procedure update_staff using cursor.execute() with CALL
                cursor.execute(
                    "CALL update_staff(%s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        int(id_to_update),
                        updated_data['name'],
                        int(updated_data['age']),
                        updated_data['gender'],
                        updated_data['address'],
                        updated_data['department'],
                        float(updated_data['salary']),
                        updated_data['date_of_joining']
                    )
                )
                cursor.execute(
                    "CALL update_staff_phone_numbers(%s, %s, %s)",
                    (
                        int(id_to_update),
                        updated_data.get('phone_no1'),  # Use value if present
                        updated_data.get('phone_no2')  # Use value if present
                    )
                )

            # Commit the transaction
            conn.commit()
            CTkMessagebox(title="Success", message="Update successful!", icon="check")

        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}", icon="cancel")
            print(f"An error occurred: {e}")

        finally:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    update_window = UpdateWindow("Data Update", 500, 200)
    update_window.mainloop()
