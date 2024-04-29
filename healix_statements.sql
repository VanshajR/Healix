CREATE TABLE Patients (
    Patient_ID SERIAL PRIMARY KEY, -- Unique identifier for each patient
    Name VARCHAR(100) NOT NULL, -- Patient's name
    Age INT NOT NULL, -- Patient's age
    Gender CHAR(1) CHECK (Gender IN ('M', 'F', 'O')), -- Patient's gender: 'M', 'F', or 'O'
    Address TEXT NOT NULL, -- Patient's address
    Password VARCHAR(100) NOT NULL, -- Patient's password (you should store hashed passwords)
    Admission_Date DATE NOT NULL, -- Date of admission
    Release_Date DATE DEFAULT NULL
);

-- Staff table
CREATE TABLE Staff (
    S_ID SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Age INTEGER NOT NULL,
    Gender CHAR(1) CHECK (Gender IN ('M', 'F', 'O')) NOT NULL,
    Address VARCHAR(200) NOT NULL,
    Department VARCHAR(100) NOT NULL,
    Salary NUMERIC(10, 2) NOT NULL,
    Date_of_Joining DATE NOT NULL
);

-- Doctors Table
CREATE TABLE Doctors (
    Doc_ID SERIAL PRIMARY KEY,
    S_ID INTEGER REFERENCES Staff(S_ID) ON DELETE CASCADE ON UPDATE CASCADE,
    Pass VARCHAR(50) NOT NULL -- Minimum length check can be handled at the application layer
);

-- Table for Patient Phone Numbers
CREATE TABLE Patient_Phone_Numbers (
    Patient_ID INT REFERENCES Patients(Patient_ID),
    Phone_Number VARCHAR(10) NOT NULL CHECK (LENGTH(Phone_Number) = 10)
);

-- Create a table for staff phone numbers
CREATE TABLE Staff_Phone_Numbers (
    Staff_ID INT REFERENCES Staff(S_ID),
    Phone_Number VARCHAR(10) NOT NULL CHECK (LENGTH(Phone_Number) = 10)
);

CREATE TABLE assignment (
    patient_id INTEGER,
    doc_id INTEGER,
    CONSTRAINT fk_patient FOREIGN KEY (patient_id) REFERENCES Patients (Patient_ID) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_doctor FOREIGN KEY (doc_id) REFERENCES Doctors (Doc_ID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE OR REPLACE FUNCTION register_patient(
    p_name VARCHAR,
    p_age INT,
    p_gender CHAR(1),
    p_address VARCHAR,
    p_phone_no1 VARCHAR,
    p_phone_no2 VARCHAR,
    p_password VARCHAR,
    p_admission_date DATE
) RETURNS INTEGER AS $$
DECLARE
    patient_id INTEGER;
BEGIN
    INSERT INTO Patients (name, age, gender, address, admission_date)
    VALUES (p_name, p_age, p_gender, p_address, p_admission_date)
    RETURNING patient_id INTO patient_id;

    -- Insert the first phone number
    IF p_phone_no1 IS NOT NULL THEN
        INSERT INTO Patient_Phone_Numbers (patient_id, phone_number)
        VALUES (patient_id, p_phone_no1);
    END IF;

    -- Insert the second phone number
    IF p_phone_no2 IS NOT NULL THEN
        INSERT INTO Patient_Phone_Numbers (patient_id, phone_number)
        VALUES (patient_id, p_phone_no2);
    END IF;
    RETURN patient_id;
END;
$$ LANGUAGE plpgsql;


Function to register a staff member
CREATE OR REPLACE FUNCTION register_staff(
    name VARCHAR,
    age INTEGER,
    gender CHAR(1),
    address TEXT,
    department VARCHAR,
    salary NUMERIC(10, 2),
    date_of_joining DATE,
    phone_no1 VARCHAR,
    phone_no2 VARCHAR
) RETURNS INTEGER AS $$
DECLARE
    staff_id INTEGER;
BEGIN
    -- Insert the staff data into the Staff table
    INSERT INTO Staff (Name, Age, Gender, Address, Department, Salary, Date_of_Joining)
    VALUES (name, age, gender, address, department, salary, date_of_joining)
    RETURNING S_ID INTO staff_id;

    -- Insert the first phone number if provided
    IF phone_no1 IS NOT NULL THEN
        INSERT INTO Staff_Phone_Numbers (S_ID, Phone_Number)
        VALUES (staff_id, phone_no1);
    END IF;

    -- Insert the second phone number if provided
    IF phone_no2 IS NOT NULL THEN
        INSERT INTO Staff_Phone_Numbers (S_ID, Phone_Number)
        VALUES (staff_id, phone_no2);
    END IF;

    -- Return the generated staff ID
    RETURN staff_id;
END;
$$ LANGUAGE plpgsql;

-- Function to register a doctor
CREATE OR REPLACE FUNCTION register_doctor(
    name VARCHAR,
    age INTEGER,
    gender CHAR(1),
    address TEXT,
    department VARCHAR,
    salary NUMERIC(10,2),
    date_of_joining DATE,
    phone_no1 VARCHAR,
    phone_no2 VARCHAR,
    password VARCHAR
) RETURNS INTEGER AS $$
DECLARE
    staff_id INTEGER;
    doctor_id INTEGER;
BEGIN
    -- Insert the doctor data into the Staff table
    staff_id := register_staff(name, age, gender, address, department, salary, date_of_joining, phone_no1, phone_no2);

    -- Generate a doctor ID
    doctor_id := generate_doctor_id();

    -- Insert doctor data into the Doctors table
    INSERT INTO Doctors (Doc_ID, S_ID, Pass)
    VALUES (doctor_id, staff_id, password);

    -- Return the generated doctor ID
    RETURN doctor_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fetch_details(
  category text,
  id_to_update integer
)
RETURNS details_record
LANGUAGE plpgsql
AS $BODY$
DECLARE
  -- Declare a refcursor
  details_cursor REFCURSOR;
  record details_record;
  query TEXT;
BEGIN
  -- Determine the query to execute based on the category input
  IF category = 'Patient' THEN
    query := 'SELECT P.Patient_ID AS id, P.Name AS name, P.Age AS age, P.Gender AS gender, P.Address AS address, NULL AS department, NULL AS salary, P.Admission_Date AS admission_date, P.Release_Date AS release_date, NULL AS date_of_joining, P.Password AS password,
              ppn.phone_number AS phone_no1,
              (SELECT phone_number FROM patient_phone_numbers WHERE patient_id = P.patient_id 
               ORDER BY phone_number OFFSET 1 ROWS FETCH NEXT 1 ROW ONLY) AS phone_no2
             FROM Patients P 
             LEFT JOIN patient_phone_numbers ppn ON P.Patient_ID = ppn.patient_id
             WHERE P.Patient_ID = $1 
             LIMIT 1';
  ELSIF category = 'Doctor' THEN
    query := 'SELECT D.Doc_ID AS id, S.Name AS name, S.Age AS age, S.Gender AS gender, S.Address AS address, S.Department AS department, S.Salary AS salary, NULL AS admission_date, NULL AS release_date, S.Date_of_Joining AS date_of_joining, D.Pass AS password,
              dppn.phone_number AS phone_no1,
              (SELECT phone_number FROM staff_phone_numbers WHERE s_id = D.S_ID 
               ORDER BY phone_number OFFSET 1 ROWS FETCH NEXT 1 ROW ONLY) AS phone_no2
             FROM Doctors D JOIN Staff S ON D.S_ID = S.S_ID
             LEFT JOIN staff_phone_numbers dppn ON D.S_ID = dppn.s_id
             WHERE D.Doc_ID = $1 
             LIMIT 1';
  ELSIF category = 'Staff' THEN
    query := 'SELECT S.S_ID AS id, S.Name AS name, S.Age AS age, S.Gender AS gender, S.Address AS address, S.Department AS department, S.Salary AS salary, NULL AS admission_date, NULL AS release_date, S.Date_of_Joining AS date_of_joining, NULL AS password,
              sppn.phone_number AS phone_no1,
              (SELECT phone_number FROM staff_phone_numbers WHERE s_id = S.S_ID 
               ORDER BY phone_number OFFSET 1 ROWS FETCH NEXT 1 ROW ONLY) AS phone_no2
             FROM Staff S 
             LEFT JOIN staff_phone_numbers sppn ON S.S_ID = sppn.s_id
             WHERE S.S_ID = $1 
             LIMIT 1';
  ELSE
    -- Raise an exception if the category is invalid
    RAISE EXCEPTION 'Invalid category';
  END IF;

  -- Open the cursor with the constructed query and the input parameter
  OPEN details_cursor FOR EXECUTE query USING id_to_update;

  -- Fetch a single row from the cursor and store it in the record variable
  FETCH details_cursor INTO record;

  -- Close the cursor
  CLOSE details_cursor;

  -- Return the fetched record
  RETURN record;
END;
$BODY$;



CREATE OR REPLACE PROCEDURE update_patient(
    p_patient_id INT,
    p_name VARCHAR DEFAULT NULL,
    p_age INT DEFAULT NULL,
    p_gender VARCHAR DEFAULT NULL,
    p_address VARCHAR DEFAULT NULL,
    p_password VARCHAR DEFAULT NULL,
	p_admission_date date DEFAULT NULL,
	p_release_date date DEFAULT NULL
) LANGUAGE plpgsql AS $$
BEGIN
    -- Row-level lock on the patient's record
    LOCK TABLE Patients IN ROW EXCLUSIVE MODE;
    
    -- Update the patient's details
    UPDATE Patients
    SET
        Name = COALESCE(p_name, Name),
        Age = COALESCE(p_age, Age),
        Gender = COALESCE(p_gender, Gender),
        Address = COALESCE(p_address, Address),
        Password = COALESCE(p_password, Password),
		Admission_Date = COALESCE(p_admission_date, Admission_Date),
    	Release_Date = COALESCE(p_release_date, Release_Date)
    WHERE Patient_ID = p_patient_id;

    IF NOT FOUND THEN
        -- No record found with the given ID
        RAISE EXCEPTION 'Patient with ID % not found.', p_patient_id;
    END IF;
END;
$$;


CREATE OR REPLACE PROCEDURE update_patient_phone_numbers(
  p_patient_id INTEGER,
  p_phone_no1 VARCHAR DEFAULT NULL,
  p_phone_no2 VARCHAR DEFAULT NULL
)
LANGUAGE plpgsql
AS $BODY$
BEGIN
  -- Delete existing phone numbers for the patient
  DELETE FROM patient_phone_numbers
  WHERE patient_id = p_patient_id;

  -- Insert the provided phone numbers (if not null)
  IF p_phone_no1 IS NOT NULL THEN
    INSERT INTO patient_phone_numbers (patient_id, phone_number) VALUES (p_patient_id, p_phone_no1);
  END IF;

  IF p_phone_no2 IS NOT NULL THEN
    INSERT INTO patient_phone_numbers (patient_id, phone_number) VALUES (p_patient_id, p_phone_no2);
  END IF;
END;
$BODY$;



CREATE OR REPLACE PROCEDURE update_staff(
    s_staff_id INT,
    s_name VARCHAR DEFAULT NULL,
    s_age INT DEFAULT NULL,
    s_gender VARCHAR DEFAULT NULL,
    s_address VARCHAR DEFAULT NULL,
	s_department VARCHAR DEFAULT NULL,
	s_salary NUMERIC(15,2) DEFAULT NULL,
	s_joining_date date DEFAULT NULL
) LANGUAGE plpgsql AS $$
BEGIN
    -- Row-level lock on the patient's record
    LOCK TABLE Staff IN ROW EXCLUSIVE MODE;
    
    -- Update the patient's details
    UPDATE Staff
    SET
        Name = COALESCE(s_name, Name),
        Age = COALESCE(s_age, Age),
        Gender = COALESCE(s_gender, Gender),
        Address = COALESCE(s_address, Address),
		Department = COALESCE(s_department, Department),
		Salary = COALESCE(s_salary, Salary),
		date_of_joining = COALESCE(s_joining_date, date_of_joining)
    WHERE S_ID = s_staff_id;

    IF NOT FOUND THEN
        -- No record found with the given ID
        RAISE EXCEPTION 'Staff with ID % not found.', s_staff_id;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE update_doctor(
    d_doc_id INT,
    d_password VARCHAR DEFAULT NULL
) LANGUAGE plpgsql AS $$
BEGIN
    -- Row-level lock on the patient's record
    LOCK TABLE Doctors IN ROW EXCLUSIVE MODE;
    
    -- Update the patient's details
    UPDATE Doctors
    SET
        Pass = COALESCE(d_password, Pass)
    WHERE Doc_ID = d_doc_id;
    IF NOT FOUND THEN
        -- No record found with the given ID
        RAISE EXCEPTION 'Doctor with ID % not found.', d_doc_id;
    END IF;
END;
$$;


CREATE OR REPLACE PROCEDURE update_staff_phone_numbers(
  s_staff_id INTEGER,
  s_phone_no1 VARCHAR DEFAULT NULL,
  s_phone_no2 VARCHAR DEFAULT NULL
)
LANGUAGE plpgsql
AS $BODY$
BEGIN
  -- Delete existing phone numbers for the patient
  DELETE FROM staff_phone_numbers
  WHERE s_id = s_staff_id;

  -- Insert the provided phone numbers (if not null)
  IF s_phone_no1 IS NOT NULL THEN
    INSERT INTO staff_phone_numbers (s_id, phone_number) VALUES (s_staff_id, s_phone_no1);
  END IF;

  IF s_phone_no2 IS NOT NULL THEN
    INSERT INTO staff_phone_numbers (s_id, phone_number) VALUES (s_staff_id, s_phone_no2);
  END IF;
END;
$BODY$;


CREATE OR REPLACE PROCEDURE delete_patient(
    p_patient_id INT) LANGUAGE plpgsql AS $$
BEGIN
    -- Row-level lock on the staff record
    LOCK TABLE Staff IN ROW EXCLUSIVE MODE;
    
    -- Delete the staff member's record
    DELETE FROM Patients
    WHERE Patient_ID = p_patient_id;

    IF NOT FOUND THEN
        -- No record found with the given ID
        RAISE EXCEPTION 'Staff member with ID % not found.', p_patient_id;
    END IF;
END;
$$;


CREATE OR REPLACE PROCEDURE delete_doctor(
	doctor_id integer)

AS $$
BEGIN
  -- Delete the doctor record (cascade will handle dependent records)
  DELETE FROM Doctors
  WHERE Doc_ID = doctor_id;

  IF NOT FOUND THEN
    -- No record found with the given ID
    RAISE EXCEPTION 'Doctor with ID % not found.', doctor_id;
  END IF;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE PROCEDURE delete_staff(
	s_staff_id integer)
AS $$
BEGIN
  -- Delete the staff record (cascade will handle dependent records)
  DELETE FROM Staff
  WHERE S_ID = s_staff_id;

  IF NOT FOUND THEN
    -- No record found with the given ID
    RAISE EXCEPTION 'Staff with ID % not found.', s_staff_id;
  END IF;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION check_patient_login(
    patient_id_in INTEGER,
    password_in VARCHAR
)
RETURNS BOOLEAN AS $$
DECLARE
    is_valid BOOLEAN := FALSE;
BEGIN
    -- Check if the credentials match any patient
    SELECT TRUE INTO is_valid
    FROM Patients
    WHERE Patient_ID = patient_id_in AND password = password_in;
    
    RETURN is_valid;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION check_doctor_login(
    doctor_id_in INTEGER,
    password_in VARCHAR
)
RETURNS BOOLEAN AS $$
DECLARE
    is_valid BOOLEAN := FALSE;
BEGIN
    -- Check if the credentials match any doctor
    SELECT TRUE INTO is_valid
    FROM Doctors
    WHERE Doc_ID = doctor_id_in AND pass = password_in;
    
    RETURN is_valid;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE assign_doctor_to_patient(p_patient_id INTEGER, p_doc_id INTEGER) AS $$
BEGIN
    INSERT INTO assignment (patient_id, doc_id) VALUES (p_patient_id, p_doc_id);
    COMMIT;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION upper_trigger_staff()
RETURNS TRIGGER AS $$
BEGIN
    NEW.name := UPPER(NEW.name);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER upper_trigger_staff
BEFORE INSERT OR UPDATE OF name ON Staff
FOR EACH ROW
EXECUTE FUNCTION upper_trigger_staff();

CREATE OR REPLACE FUNCTION upper_trigger_patient()
RETURNS TRIGGER AS $$
BEGIN
    NEW.name := UPPER(NEW.name);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER upper_trigger_patient
BEFORE INSERT OR UPDATE OF name ON Patient
FOR EACH ROW
EXECUTE FUNCTION upper_trigger_patient();