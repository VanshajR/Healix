import customtkinter as cust
from CTkMessagebox import CTkMessagebox
import psycopg2
import os
import urllib.parse as up
from dotenv import load_dotenv
from admin import AdminWindow


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
class LoginWindow(cust.CTk):
    def __init__(self, title, width, height):
        super().__init__()

        # Initialize the main window
        self.title(title)
        self.geometry(f"{width}x{height}")

        # Create a frame for the login inputs
        self.login_frame = cust.CTkFrame(self)
        self.login_frame.pack(pady=20)

        # Drop-down menu to select the login type
        self.login_type_label = cust.CTkLabel(self.login_frame, text="Login Type:")
        self.login_type_label.grid(row=0, column=0, padx=10, pady=5)
        self.login_type = cust.CTkOptionMenu(
            self.login_frame, values=["Patient", "Doctor"]
        )
        self.login_type.grid(row=0, column=1, padx=10, pady=5)
        self.login_type.set("Patient")  # Default to "Patient"

        # Label and entry for user_id
        self.user_id_label = cust.CTkLabel(self.login_frame, text="User ID:")
        self.user_id_label.grid(row=1, column=0, padx=10, pady=5)
        self.user_id_entry = cust.CTkEntry(self.login_frame)
        self.user_id_entry.grid(row=1, column=1, padx=10, pady=5)

        # Label and entry for password
        self.password_label = cust.CTkLabel(self.login_frame, text="Password:")
        self.password_label.grid(row=2, column=0, padx=10, pady=5)
        self.password_entry = cust.CTkEntry(self.login_frame, show="*")
        self.password_entry.grid(row=2, column=1, padx=10, pady=5)

        # Button to perform login
        self.login_button = cust.CTkButton(self.login_frame, text="Login", command=self.perform_login)
        self.login_button.grid(row=3, columnspan=2, padx=10, pady=10)

    def perform_login(self):
        # Get login type
        login_type = self.login_type.get()
        # Connect to the database
        conn = connect_to_database()
        cursor = conn.cursor()

        try:
            # Call the appropriate PL/SQL function based on the login type
            #If admin account
            if self.user_id_entry.get()==os.getenv("ADMIN_ID"):
                if self.password_entry.get()==os.getenv("ADMIN_PASSWORD"):
                    login_window = AdminWindow("Admin Control Panel", 300, 280)
                    login_window.mainloop()
                    return
                else:
                    CTkMessagebox(title="Login Failed", message="Invalid user_id or password.", icon="warning")
                    return
            else:
                #Get user_id, and password from the entries if not admin
                user_id = self.user_id_entry.get()
                password = self.password_entry.get()
                if login_type == "Patient":
                    cursor.execute("SELECT check_patient_login(%s, %s)", (int(user_id), password))
                elif login_type == "Doctor":
                    cursor.execute("SELECT check_doctor_login(%s, %s)", (int(user_id), password))



            # Fetch the result
            result = cursor.fetchone()
            is_valid = result[0] if result else False

            # Determine the user type and display appropriate message
            if is_valid:
                if login_type == "Patient":
                    CTkMessagebox(title="Login Successful", message="You are logged in as a patient.", icon="info")
                elif login_type == "Doctor":
                    CTkMessagebox(title="Login Successful", message="You are logged in as a doctor.", icon="info")
            else:
                CTkMessagebox(title="Login Failed", message="Invalid user_id or password.", icon="warning")

        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}", icon="cancel")
            print(f"An error occurred: {e}")

        finally:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    login_window = LoginWindow("Login", 300, 230)
    login_window.mainloop()