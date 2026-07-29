from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'karuppan_secret_key'

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="college_portal"
)
cursor = db.cursor()

# Home redirects to login
@app.route('/')
def home():
    return redirect(url_for('login'))

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        userid = request.form['userid'].strip()
        password = request.form['password'].strip()
        role = request.form['role'].strip().lower()

        cursor.execute("SELECT * FROM users WHERE userid=%s AND password=%s AND role=%s", (userid, password, role))
        user = cursor.fetchone()

        if user:
            session['userid'] = userid
            session['role'] = role
            if role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif role == 'hod':
                return redirect(url_for('hod_dashboard'))
            elif role == 'student':
                return redirect(url_for('student_dashboard'))
        else:
            msg = 'Invalid user ID or password'

    return render_template('login.html', msg=msg)

# Admin Dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'role' in session and session['role'] == 'admin':
        return render_template('admin_dashboard.html', userid=session['userid'])
    return redirect(url_for('login'))

# Add Student
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if 'role' in session and session['role'] == 'admin':
        if request.method == 'POST':
            name = request.form['name'].strip()
            userid = request.form['userid'].strip()
            password = request.form['password'].strip()

            cursor.execute("INSERT INTO students (name, userid, password) VALUES (%s, %s, %s)", (name, userid, password))
            cursor.execute("INSERT INTO users (userid, password, role) VALUES (%s, %s, %s)", (userid, password, 'student'))
            db.commit()
            return redirect(url_for('admin_dashboard'))
        return render_template('add_student.html')
    return redirect(url_for('login'))

# Add HOD
@app.route('/add_hod', methods=['GET', 'POST'])
def add_hod():
    if 'role' in session and session['role'] == 'admin':
        if request.method == 'POST':
            name = request.form['name'].strip()
            userid = request.form['userid'].strip()
            password = request.form['password'].strip()

            cursor.execute("INSERT INTO hods (name, userid, password) VALUES (%s, %s, %s)", (name, userid, password))
            cursor.execute("INSERT INTO users (userid, password, role) VALUES (%s, %s, %s)", (userid, password, 'hod'))
            db.commit()
            return redirect(url_for('admin_dashboard'))
        return render_template('add_hod.html')
    return redirect(url_for('login'))

# HOD Dashboard
@app.route('/hod_dashboard')
def hod_dashboard():
    if 'role' in session and session['role'] == 'hod':
        return render_template('dashboard_hod.html', userid=session['userid'])
    return redirect(url_for('login'))

# Student Dashboard
@app.route('/student_dashboard')
def student_dashboard():
    if 'role' in session and session['role'] == 'student':
        return render_template('dashboard_student.html', userid=session['userid'])
    return redirect(url_for('login'))

# Upload Document Page for admin
@app.route('/upload_document', methods=['GET', 'POST'])
def upload_document():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        student_id = request.form['student_id']
        document_type = request.form['document_type']
        file = request.files['document']
        filename = file.filename
        file_data = file.read()

        # Fetch student name for the given student_id (optional)
        cursor.execute("SELECT name FROM students WHERE userid = %s", (student_id,))
        result = cursor.fetchone()
        student_name = result[0] if result else None

        cursor.execute("""
            INSERT INTO student_documents (student_id, student_name, document_type, filename, file_data)
            VALUES (%s, %s, %s, %s, %s)
        """, (student_id, student_name, document_type, filename, file_data))
        db.commit()

        flash("File uploaded successfully!", "success")
        return redirect(url_for('upload_document'))

    return render_template('upload_form.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
