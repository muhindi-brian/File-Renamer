import os
import re
import mysql.connector
from flask import Flask, request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename
import pdfplumber
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure paths and database from environment variables
INVOICE_PATH = os.getenv('INVOICE_PATH')
ESTIMATE_PATH = os.getenv('ESTIMATE_PATH')
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

# Create necessary directories
os.makedirs(INVOICE_PATH, exist_ok=True)
os.makedirs(ESTIMATE_PATH, exist_ok=True)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def log_activity(activity):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO activity_log (activity) VALUES (%s)", (activity,))
        connection.commit()
    except Exception as e:
        print(f"Error logging activity: {e}")
    finally:
        cursor.close()
        connection.close()

def log_error(error_message):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO error_log (error_message) VALUES (%s)", (error_message,))
        connection.commit()
    except Exception as e:
        print(f"Error logging error: {e}")
    finally:
        cursor.close()
        connection.close()

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
        log_error(f"Error extracting info from {pdf_path}: {e}")
    return client_name, doc_number

@app.route('/', methods=['GET', 'POST'])
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
                flash(f"File uploaded and renamed to {new_filename} in {target_folder}", 'success')
                log_activity(f"Uploaded and renamed file to {new_filename}")
                return redirect(url_for('upload_file'))
            else:
                flash("Could not extract necessary information from the file", 'danger')
                os.remove(temp_file_path)  # Clean up temp file
                return redirect(request.url)

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
