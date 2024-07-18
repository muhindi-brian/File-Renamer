import os
import re
import mysql.connector
from flask import Flask, request, redirect, url_for, render_template, flash, session
from werkzeug.utils import secure_filename
import pdfplumber
from dotenv import load_dotenv
from datetime import datetime
import bcrypt


# Load environment variables from .env file
load_dotenv()

# Configure paths and database credentials from environment variables
INVOICE_PATH = os.getenv('INVOICE_PATH')
ESTIMATE_PATH = os.getenv('ESTIMATE_PATH')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

# Create necessary directories
os.makedirs(INVOICE_PATH, exist_ok=True)
os.makedirs(ESTIMATE_PATH, exist_ok=True)

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def extract_info(pdf_path, keyword_client, keyword_number):
    client_name = None
    doc_number = None
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    lines = text.split('\n')
                    for i, line in enumerate(lines):
                        if keyword_client in line:
                            client_name = lines[i + 1].strip()
                        if keyword_number in line:
                            doc_number = line.split(keyword_number)[-1].strip()
                            break
    except Exception as e:
        log_activity('Error extracting info', str(e), pdf_path)
    return client_name, doc_number


def log_activity(activity, user_data, url):
    connection = mysql.connector.connect(
        host='localhost',
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = connection.cursor()
    cursor.execute("INSERT INTO uploads (activity, user_data, url, timestamp) VALUES (%s, %s, %s, %s)",
                   (activity, user_data, url, datetime.now()))
    connection.commit()
    cursor.close()
    connection.close()


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        connection = mysql.connector.connect(
            host='localhost',
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        connection.commit()
        cursor.close()
        connection.close()

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = mysql.connector.connect(
            host='localhost',
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = connection.cursor()
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))  # Redirect to dashboard
        else:
            flash('Invalid credentials', 'danger')

    return render_template('login.html')

#Shows the username on header
@app.route('/')
def dashboard():
    if 'username' not in session:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('login'))
    username = session['username']
    return render_template('dashboard.html', username=username)  # Pass username to template

# @app.route('/dashboard')
# def dashboard():
#     if 'username' not in session:
#         flash('You need to log in first.', 'warning')
#         return redirect(url_for('login'))
#     return render_template('dashboard.html')  # Render your dashboard template

@app.route('/view_activity', methods=['GET', 'POST'])
def view_activity():
    if 'username' not in session:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('login'))
    
    username = session['username']
    connection = mysql.connector.connect(
        host='localhost',
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = connection.cursor()
    
    # Initialize query and parameters
    query = "SELECT activity, user_data, url, timestamp FROM uploads WHERE user_data = %s"
    params = [username]

    # Handle search functionality
    search_term = request.args.get('search', '')
    if search_term:
        query += " AND (activity LIKE %s OR url LIKE %s)"
        params.extend(['%' + search_term + '%', '%' + search_term + '%'])

    cursor.execute(query + " ORDER BY timestamp DESC", tuple(params))
    activities = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('activity.html', activities=activities, search_term=search_term)

# @app.route('/view_activity')
# def view_activity():
#     if 'username' not in session:
#         flash('You need to log in first.', 'warning')
#         return redirect(url_for('login'))
    
#     username = session['username']
#     print(f"Current logged-in user: {username}")  # Debugging

#     connection = mysql.connector.connect(
#         host='localhost',
#         user=DB_USER,
#         password=DB_PASSWORD,
#         database=DB_NAME
#     )
#     cursor = connection.cursor()
#     cursor.execute("SELECT activity, user_data, url, timestamp FROM uploads WHERE user_data = %s ORDER BY timestamp DESC", (username,))
#     activities = cursor.fetchall()
#     cursor.close()
#     connection.close()

#     # Debugging: print fetched activities
#     print(f"Fetched activities: {activities}")  # Debugging
#     # print(f"Fetched activities for {username}: {activities}")
    
#     return render_template('activity.html', activities=activities)

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Get form data with fallback to avoid KeyError
        full_name = request.form.get('full_name', '')
        date_of_birth = request.form.get('date_of_birth', '')
        gender = request.form.get('gender', '')
        nationality = request.form.get('nationality', '')
        id_number = request.form.get('id_number', '')
        national_id_type = request.form.get('national_id_type', '')
        expiry_date = request.form.get('expiry_date', '')
        email = request.form.get('email', '')
        phone_number = request.form.get('phone_number', '')
        address_street = request.form.get('address_street', '')
        address_city = request.form.get('address_city', '')
        address_state = request.form.get('address_state', '')
        address_zip = request.form.get('address_zip', '')
        address_country = request.form.get('address_country', '')
        occupation = request.form.get('occupation', '')
        company_name = request.form.get('company_name', '')

        # Create database connection
        db_connection = get_db_connection()
        cursor = db_connection.cursor()

        # Find the user ID based on username
        cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
        user = cursor.fetchone()

        if user:
            user_id = user[0]
            # Update user profile
            cursor.execute("""
                INSERT INTO user_profiles (user_id, full_name, date_of_birth, gender, nationality, id_number, national_id_type, expiry_date, email, phone_number, address_street, address_city, address_state, address_zip, address_country, occupation, company_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                full_name = VALUES(full_name),
                date_of_birth = VALUES(date_of_birth),
                gender = VALUES(gender),
                nationality = VALUES(nationality),
                id_number = VALUES(id_number),
                national_id_type = VALUES(national_id_type),
                expiry_date = VALUES(expiry_date),
                email = VALUES(email),
                phone_number = VALUES(phone_number),
                address_street = VALUES(address_street),
                address_city = VALUES(address_city),
                address_state = VALUES(address_state),
                address_zip = VALUES(address_zip),
                address_country = VALUES(address_country),
                occupation = VALUES(occupation),
                company_name = VALUES(company_name)
            """, (user_id, full_name, date_of_birth, gender, nationality, id_number, national_id_type, expiry_date, email, phone_number, address_street, address_city, address_state, address_zip, address_country, occupation, company_name))
            db_connection.commit()
            flash('Profile updated successfully', 'success')
        else:
            flash('User not found', 'danger')

        cursor.close()  # Close the cursor
        db_connection.close()  # Close the database connection

    # Fetch user profile data
    db_connection = get_db_connection()
    cursor = db_connection.cursor()
    cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
    user = cursor.fetchone()

    user_data = None  # Initialize user_data

    if user:
        user_id = user[0]
        cursor.execute("SELECT * FROM user_profiles WHERE user_id = %s", (user_id,))
        user_data = cursor.fetchone()  # Get user profile data
    else:
        user_data = None

    cursor.close()  # Close the cursor
    db_connection.close()  # Close the database connection
    return render_template('profile.html', user_data=user_data)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        new_username = request.form.get('username', '')
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Create database connection
        db_connection = get_db_connection()
        cursor = db_connection.cursor()

        # Verify current password
        cursor.execute("SELECT password FROM users WHERE username = %s", (session['username'],))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(current_password.encode('utf-8'), user[0].encode('utf-8')):
            # Check if new passwords match
            if new_password == confirm_password:
                hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

                # Update username and password
                cursor.execute("UPDATE users SET username = %s, password = %s WHERE username = %s",
                               (new_username, hashed_password, session['username']))
                db_connection.commit()

                # Update session username
                session['username'] = new_username

                flash('Settings updated successfully', 'success')
            else:
                flash('New passwords do not match', 'danger')
        else:
            flash('Current password is incorrect', 'danger')

        cursor.close()  # Close the cursor
        db_connection.close()  # Close the database connection

    return render_template('settings.html')



@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            temp_file_path = os.path.join(INVOICE_PATH, filename)  # Temporary path for saving file

            file.save(temp_file_path)

            if 'INV-' in filename:
                keyword_client = 'Bill To'
                keyword_number = 'Invoice#'
                target_folder = INVOICE_PATH
            elif 'EST-' in filename:
                keyword_client = 'Bill To'
                keyword_number = '# EST-'
                target_folder = ESTIMATE_PATH
            else:
                flash('Unknown document type', 'danger')
                return redirect(request.url)

            client_name, doc_number = extract_info(temp_file_path, keyword_client, keyword_number)
            if client_name and doc_number:
                new_filename = sanitize_filename(f"{client_name} {doc_number}.pdf")
                new_file_path = os.path.join(target_folder, new_filename)

                if os.path.exists(new_file_path):
                    flash(f"A file named '{new_filename}' already exists. Please upload a new file.", 'warning')
                    os.remove(temp_file_path)  # Clean up temp file
                    return redirect(request.url)

                os.rename(temp_file_path, new_file_path)
                log_activity('File uploaded and renamed', client_name, new_file_path)
                flash(f"File uploaded and renamed to {new_filename} in {target_folder}", 'success')
                return redirect(url_for('upload_file'))
            else:
                flash("Could not extract necessary information from the file", 'danger')
                os.remove(temp_file_path)  # Clean up temp file
                return redirect(request.url)

    return render_template('index.html')

@app.route('/manifest.json')
def manifest():
    return app.send_static_file('manifest.json')

@app.route('/service-worker.js')
def service_worker():
    return app.send_static_file('service-worker.js')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

    app.run(debug=True)
