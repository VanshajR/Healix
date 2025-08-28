"""
Simple Flask Web Interface for Healix
This provides a web-based alternative to the GUI application
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2
import os
import urllib.parse as up
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'healix-secret-key-change-in-production')

def connect_to_database():
    """Connect to PostgreSQL database"""
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

@app.route('/')
def index():
    """Home page with login options"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for patients and doctors"""
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        login_type = request.form.get('login_type')
        
        # Admin login check
        if user_id == os.getenv("ADMIN_ID") and password == os.getenv("ADMIN_PASSWORD"):
            session['user_type'] = 'admin'
            session['user_id'] = user_id
            return redirect(url_for('admin_dashboard'))
        
        # Database login check
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            if login_type == 'Patient':
                cursor.execute("SELECT check_patient_login(%s, %s)", (int(user_id), password))
                result = cursor.fetchone()
                if result and result[0]:
                    session['user_type'] = 'patient'
                    session['user_id'] = user_id
                    return redirect(url_for('patient_dashboard'))
                    
            elif login_type == 'Doctor':
                cursor.execute("SELECT check_doctor_login(%s, %s)", (int(user_id), password))
                result = cursor.fetchone()
                if result and result[0]:
                    session['user_type'] = 'doctor'
                    session['user_id'] = user_id
                    return redirect(url_for('doctor_dashboard'))
            
            cursor.close()
            conn.close()
            flash('Invalid login credentials', 'error')
            
        except Exception as e:
            flash(f'Database error: {str(e)}', 'error')
    
    return render_template('login.html')

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard"""
    if session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html')

@app.route('/patient')
def patient_dashboard():
    """Patient dashboard"""
    if session.get('user_type') != 'patient':
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    
    # Get patient info and assigned doctors
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        
        # Get assigned doctors
        cursor.execute("""
            SELECT d.doc_id, s.name 
            FROM assignment ad 
            JOIN doctors d ON ad.doc_id = d.doc_id 
            JOIN staff s ON d.s_id = s.s_id 
            WHERE ad.patient_id = %s
        """, (int(user_id),))
        assigned_doctors = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('patient_dashboard.html', 
                             user_id=user_id, 
                             assigned_doctors=assigned_doctors)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('login'))

@app.route('/doctor')
def doctor_dashboard():
    """Doctor dashboard"""
    if session.get('user_type') != 'doctor':
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    return render_template('doctor_dashboard.html', user_id=user_id)

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    app.run(host='0.0.0.0', port=5000, debug=True)