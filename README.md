# Healix

Healix is a python based hospital management project, which leverages customtkinter GUI and PostgreSQL and plpgSQL functions and procedures to provide CRUD operations. An Object Oriented approach has been followed throughout the python code for the GUI. 

## Features
- Manage records of patients, doctors and other staff
- Assign doctors to patients
- Interactive UI to manipulate records
- Robust PostgreSQL architecture that ensures data integrity
- Data filtering built into the code to ensure correctness
- GUI based actions for ease of use, implemented via Object Oriented Programming principles for organised and smooth functioning 

## Prerequisites

Before setting up Healix, ensure you have the following installed:

- Python 3.10
- PostgreSQL 12 or higher
- `pip` (Python package manager)


## Project Setup:

1. **Clone the Repository:**:

 ```bash
 git clone https://github.com/VanshajR/Healix
 cd Healix
```

2. **Setup a PostgreSQL database:**
Run the statements provided in `healix_statements.sql` in the database

3. **Setup the environment file:**
Create a .env file in the project file with the following content:

```bash
DATABASE_URL=<Your PostgreSQL URI>
ADMIN_ID=<Admin Account ID>
ADMIN_PASSWORD=<Admin Account Password>
```

4. **Install dependancies:**

```bash
pip install -r requirements.txt
```

5. **Run the files:** 
Run the `admin.py` file to enter some records for patients, doctors and staff:

```bash
python admin.py
```
This program executes the GUI for manipulation of all records and assignment of doctors.

Run the `main.py` file to login as a patient or a doctor:

```bash
python main.py
```
This program executes the GUI for the login window.

## Project Structure:  

```bash
Healix/    
├── admin.py                    # Admin functionalities   
├── assigndoctor.py             # Assign doctors to patients    
├── deletedata.py               # Remove records from the database    
├── docandstaffregistration.py  # Doctor and staff registration    
├── guiobjects.py               # GUI components and utilities    
├── healix_statements.sql       # Database setup SQL script    
├── main.py                     # Entry point for the application    
├── patientregistration.py      # Patient registration logic    
├── plsql statements            # Additional PL/pgSQL scripts    
├── updatedetails.py            # Update existing records    
├── viewassignments.py          # View doctor-patient assignments    
└── viewdetails.py              # View patient and staff details    
```

## License
This project is licensed under the BSD 3-Clause License. See the LICENSE file for details.
