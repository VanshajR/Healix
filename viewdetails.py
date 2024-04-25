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

class DataRetrievalWindow(cust.CTk):
    def __init__(self, title, width, height):
        super().__init__()

        # Initialize the main window
        self.title(title)
        self.geometry(f"{width}x{height}")

        # Create a frame for the buttons
        self.button_frame = cust.CTkFrame(self)
        self.button_frame.pack(pady=20)

        # Create buttons to fetch details of doctors, staff, or patients
        self.doctor_button = cust.CTkButton(
            self.button_frame, text="Fetch Doctor Details", command=self.fetch_doctor_details
        )
        self.doctor_button.pack(side=cust.LEFT, padx=10)

        self.staff_button = cust.CTkButton(
            self.button_frame, text="Fetch Staff Details", command=self.fetch_staff_details
        )
        self.staff_button.pack(side=cust.LEFT, padx=10)

        self.patient_button = cust.CTkButton(
            self.button_frame, text="Fetch Patient Details", command=self.fetch_patient_details
        )
        self.patient_button.pack(side=cust.LEFT, padx=10)

        # Create input frame
        self.input_frame = cust.CTkFrame(self)
        self.input_frame.pack(pady=20)

        # Label and entry for ID/Name
        self.label_id_name = cust.CTkLabel(self.input_frame, text="Enter ID or Name (leave blank for all):")
        self.label_id_name.grid(row=0, column=0, padx=10, pady=5)
        self.entry_id_name = cust.CTkEntry(self.input_frame)
        self.entry_id_name.grid(row=0, column=1, padx=10, pady=5)

        # Create options to fetch one, multiple, or all records
        self.fetch_option = cust.CTkOptionMenu(
            self.input_frame, values=["Fetch One", "Fetch Multiple", "Fetch All"]
        )
        self.fetch_option.grid(row=1, column=1, padx=10, pady=5)

        # Set default value
        self.fetch_option.set("Fetch All")

    def fetch_doctor_details(self):
        user_input = self.entry_id_name.get().strip()
        fetch_option = self.fetch_option.get()

        conn = None
        cursor = None
        try:
            conn = connect_to_database()
            cursor = conn.cursor()

            # Determine the query based on fetch option and user input
            if fetch_option == "Fetch One":
                cursor.execute("""
                    SELECT D.Doc_ID, S.Name, S.Age, S.Gender, S.Address, S.Department, S.Salary, S.Date_of_Joining, 
                    SP.Phone_Number AS Phone_Number_1, SP2.Phone_Number AS Phone_Number_2
                    FROM Doctors D
                    JOIN Staff S ON D.S_ID = S.S_ID
                    LEFT JOIN (
                        SELECT S_ID, Phone_Number, ROW_NUMBER() OVER (PARTITION BY S_ID ORDER BY Phone_Number) AS rn
                        FROM Staff_Phone_Numbers
                    ) AS SP ON S.S_ID = SP.S_ID AND SP.rn = 1
                    LEFT JOIN (
                        SELECT S_ID, Phone_Number, ROW_NUMBER() OVER (PARTITION BY S_ID ORDER BY Phone_Number) AS rn
                        FROM Staff_Phone_Numbers
                    ) AS SP2 ON S.S_ID = SP2.S_ID AND SP2.rn = 2
                    WHERE D.Doc_ID::text = %s OR S.Name ILIKE %s
                """, (user_input, f"%{user_input}%"))
            elif fetch_option == "Fetch Multiple":
                cursor.execute("""
                    SELECT D.Doc_ID, S.Name, S.Age, S.Gender, S.Address, S.Department, S.Salary, S.Date_of_Joining, 
                    SP.Phone_Number AS Phone_Number_1, SP2.Phone_Number AS Phone_Number_2
                    FROM Doctors D
                    JOIN Staff S ON D.S_ID = S.S_ID
                    LEFT JOIN (
                        SELECT S_ID, Phone_Number, ROW_NUMBER() OVER (PARTITION BY S_ID ORDER BY Phone_Number) AS rn
                        FROM Staff_Phone_Numbers
                    ) AS SP ON S.S_ID = SP.S_ID AND SP.rn = 1
                    LEFT JOIN (
                        SELECT S_ID, Phone_Number, ROW_NUMBER() OVER (PARTITION BY S_ID ORDER BY Phone_Number) AS rn
                        FROM Staff_Phone_Numbers
                    ) AS SP2 ON S.S_ID = SP2.S_ID AND SP2.rn = 2
                    WHERE D.Doc_ID::text ILIKE %s OR S.Name ILIKE %s
                """, (f"%{user_input}%", f"%{user_input}%"))
            elif fetch_option == "Fetch All":
                cursor.execute("""
                    SELECT D.Doc_ID, S.Name, S.Age, S.Gender, S.Address, S.Department, S.Salary, S.Date_of_Joining, 
                    SP.Phone_Number AS Phone_Number_1, SP2.Phone_Number AS Phone_Number_2
                    FROM Doctors D
                    JOIN Staff S ON D.S_ID = S.S_ID
                    LEFT JOIN (
                        SELECT S_ID, Phone_Number, ROW_NUMBER() OVER (PARTITION BY S_ID ORDER BY Phone_Number) AS rn
                        FROM Staff_Phone_Numbers
                    ) AS SP ON S.S_ID = SP.S_ID AND SP.rn = 1
                    LEFT JOIN (
                        SELECT S_ID, Phone_Number, ROW_NUMBER() OVER (PARTITION BY S_ID ORDER BY Phone_Number) AS rn
                        FROM Staff_Phone_Numbers
                    ) AS SP2 ON S.S_ID = SP2.S_ID AND SP2.rn = 2
                """)  # This fetches all doctor records

            # Fetch results
            results = cursor.fetchall()

            # Display results
            self.display_results("Doctor Details", results)

        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}", icon="cancel")
            print(f"An error occurred: {e}")

        finally:
            # Close cursor and connection
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    def fetch_staff_details(self):
        user_input = self.entry_id_name.get().strip()
        fetch_option = self.fetch_option.get()

        conn = None
        cursor = None
        try:
            conn = connect_to_database()
            cursor = conn.cursor()

            # Determine the query based on fetch option and user input
            if fetch_option == "Fetch One":
                cursor.execute("""
                    SELECT S.S_ID, S.Name, S.Age, S.Gender, S.Address, S.Department, S.Salary, S.Date_of_Joining, 
                    SP.Phone_Number AS Phone_Number_1, SP2.Phone_Number AS Phone_Number_2
                    FROM Staff S
                    LEFT JOIN (
                        SELECT S_ID, Phone_Number, ROW_NUMBER() OVER (PARTITION BY S_ID ORDER BY Phone_Number) AS rn
                        FROM Staff_Phone_Numbers
                    ) AS SP ON S.S_ID = SP.S_ID AND SP.rn = 1
                    LEFT JOIN (
                        SELECT S_ID, Phone_Number, ROW_NUMBER() OVER (PARTITION BY S_ID ORDER BY Phone_Number) AS rn
                        FROM Staff_Phone_Numbers
                    ) AS SP2 ON S.S_ID = SP2.S_ID AND SP2.rn = 2
                    WHERE S.S_ID::text = %s OR S.Name ILIKE %s
                """, (user_input, f"%{user_input}%"))
            elif fetch_option == "Fetch Multiple":
                cursor.execute("""
                    SELECT S.S_ID, S.Name, S.Age, S.Gender, S.Address, S.Department, S.Salary, S.Date_of_Joining, 
                    SP.Phone_Number AS Phone_Number_1, SP2.Phone_Number AS Phone_Number_2
                    FROM Staff S
                    LEFT JOIN (
                        SELECT S_ID, Phone_Number, ROW_NUMBER() OVER (PARTITION BY S_ID ORDER BY Phone_Number) AS rn
                        FROM Staff_Phone_Numbers
                    ) AS SP ON S.S_ID = SP.S_ID AND SP.rn = 1
                    LEFT JOIN (
                        SELECT S_ID, Phone_Number, ROW_NUMBER() OVER (PARTITION BY S_ID ORDER BY Phone_Number) AS rn
                        FROM Staff_Phone_Numbers
                    ) AS SP2 ON S.S_ID = SP2.S_ID AND SP2.rn = 2
                    WHERE S.S_ID::text ILIKE %s OR S.Name ILIKE %s
                """, (f"%{user_input}%", f"%{user_input}%"))
            elif fetch_option == "Fetch All":
                cursor.execute("""
                    SELECT S.S_ID, S.Name, S.Age, S.Gender, S.Address, S.Department, S.Salary, S.Date_of_Joining, 
                    SP.Phone_Number AS Phone_Number_1, SP2.Phone_Number AS Phone_Number_2
                    FROM Staff S
                    LEFT JOIN (
                        SELECT S_ID, Phone_Number, ROW_NUMBER() OVER (PARTITION BY S_ID ORDER BY Phone_Number) AS rn
                        FROM Staff_Phone_Numbers
                    ) AS SP ON S.S_ID = SP.S_ID AND SP.rn = 1
                    LEFT JOIN (
                        SELECT S_ID, Phone_Number, ROW_NUMBER() OVER (PARTITION BY S_ID ORDER BY Phone_Number) AS rn
                        FROM Staff_Phone_Numbers
                    ) AS SP2 ON S.S_ID = SP2.S_ID AND SP2.rn = 2
                """)  # This fetches all staff records

            # Fetch results
            results = cursor.fetchall()

            # Display results
            self.display_results("Staff Details", results)

        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}", icon="cancel")
            print(f"An error occurred: {e}")

        finally:
            # Close cursor and connection
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    def fetch_patient_details(self):
        user_input = self.entry_id_name.get().strip()
        fetch_option = self.fetch_option.get()

        conn = None
        cursor = None
        try:
            conn = connect_to_database()
            cursor = conn.cursor()

            # Determine the query based on fetch option and user input
            if fetch_option == "Fetch One":
                cursor.execute("""
                    SELECT P.Patient_ID, P.Name, P.Age, P.Gender, P.Address, P.Admission_Date,
                    PP.Phone_Number AS Phone_Number_1, PP2.Phone_Number AS Phone_Number_2
                    FROM Patients P
                    LEFT JOIN (
                        SELECT Patient_ID, Phone_Number, ROW_NUMBER() OVER (PARTITION BY Patient_ID ORDER BY Phone_Number) AS rn
                        FROM Patient_Phone_Numbers
                    ) AS PP ON P.Patient_ID = PP.Patient_ID AND PP.rn = 1
                    LEFT JOIN (
                        SELECT Patient_ID, Phone_Number, ROW_NUMBER() OVER (PARTITION BY Patient_ID ORDER BY Phone_Number) AS rn
                        FROM Patient_Phone_Numbers
                    ) AS PP2 ON P.Patient_ID = PP2.Patient_ID AND PP2.rn = 2
                    WHERE P.Patient_ID::text = %s OR P.Name ILIKE %s
                """, (user_input, f"%{user_input}%"))
            elif fetch_option == "Fetch Multiple":
                cursor.execute("""
                    SELECT P.Patient_ID, P.Name, P.Age, P.Gender, P.Address, P.Admission_Date,
                    PP.Phone_Number AS Phone_Number_1, PP2.Phone_Number AS Phone_Number_2
                    FROM Patients P
                    LEFT JOIN (
                        SELECT Patient_ID, Phone_Number, ROW_NUMBER() OVER (PARTITION BY Patient_ID ORDER BY Phone_Number) AS rn
                        FROM Patient_Phone_Numbers
                    ) AS PP ON P.Patient_ID = PP.Patient_ID AND PP.rn = 1
                    LEFT JOIN (
                        SELECT Patient_ID, Phone_Number, ROW_NUMBER() OVER (PARTITION BY Patient_ID ORDER BY Phone_Number) AS rn
                        FROM Patient_Phone_Numbers
                    ) AS PP2 ON P.Patient_ID = PP2.Patient_ID AND PP2.rn = 2
                    WHERE P.Patient_ID::text ILIKE %s OR P.Name ILIKE %s
                """, (f"%{user_input}%", f"%{user_input}%"))
            elif fetch_option == "Fetch All":
                cursor.execute("""
                    SELECT P.Patient_ID, P.Name, P.Age, P.Gender, P.Address, P.Admission_Date,
                    PP.Phone_Number AS Phone_Number_1, PP2.Phone_Number AS Phone_Number_2
                    FROM Patients P
                    LEFT JOIN (
                        SELECT Patient_ID, Phone_Number, ROW_NUMBER() OVER (PARTITION BY Patient_ID ORDER BY Phone_Number) AS rn
                        FROM Patient_Phone_Numbers
                    ) AS PP ON P.Patient_ID = PP.Patient_ID AND PP.rn = 1
                    LEFT JOIN (
                        SELECT Patient_ID, Phone_Number, ROW_NUMBER() OVER (PARTITION BY Patient_ID ORDER BY Phone_Number) AS rn
                        FROM Patient_Phone_Numbers
                    ) AS PP2 ON P.Patient_ID = PP2.Patient_ID AND PP2.rn = 2
                """)  # This fetches all patient records

            # Fetch results
            results = cursor.fetchall()

            # Display results if results are found
            if results:
                self.display_results("Patient Details", results)
            else:
                # Display a message if no results were found
                CTkMessagebox(title="No Results", message="No results found.", icon="warning")

        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}", icon="cancel")
            print(f"An error occurred: {e}")

        finally:
            # Close cursor and connection
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    def display_results(self, title, results):
        # Create a new window to display the results
        result_window = cust.CTkToplevel(self)
        result_window.title(title)

        # Bring the result window to the foreground
        result_window.attributes('-topmost', 1)  # Set result window as topmost

        if results:
            # Create a table to display results
            table = ttk.Treeview(result_window, columns=("1", "2", "3", "4", "5", "6", "7", "8", "9", "10"), show="headings")
            table.pack(fill="both", expand=True)

            # Define column names
            column_names = {
                "Doctor Details": ["Doc_ID", "Name", "Age", "Gender", "Address", "Department", "Salary",
                                   "Date_of_Joining", "Phone_Number_1", "Phone_Number_2"],
                "Staff Details": ["S_ID", "Name", "Age", "Gender", "Address", "Department", "Salary",
                                  "Date_of_Joining", "Phone_Number_1", "Phone_Number_2"],
                "Patient Details": ["Patient_ID", "Name", "Age", "Gender", "Address", "Admission_Date",
                                    "Phone_Number_1", "Phone_Number_2"]
            }

            style = ttk.Style(result_window)
            style.configure("Treeview", font=("Arial", 12))  # Adjust the font as needed

            # Setup table columns
            for i, col in enumerate(column_names[title], start=1):
                table.heading(f"{i}", text=col)
                table.column(f"{i}", width=150)

            # Populate the table with results
            for result in results:
                table.insert("", cust.END, values=result)

        else:
            # Display a message if no results were found
            CTkMessagebox(title="No Results", message="No results found.", icon="warning")

if __name__ == "__main__":
    data_retrieval_window = DataRetrievalWindow("Data Retrieval", 500, 200)
    data_retrieval_window.resizable(width=False, height=False)
    data_retrieval_window.mainloop()
