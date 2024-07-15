import os
import re
from flask import Flask, request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename
import pdfplumber

# Configure paths
INVOICE_PATH = r"C:\Users\brian\OneDrive\Desktop\MOJOKDEVKE\CBSG-ERP\INVOICES"
ESTIMATE_PATH = r"C:\Users\brian\OneDrive\Desktop\MOJOKDEVKE\CBSG-ERP\PFI"

# Ensure directories exist
os.makedirs(INVOICE_PATH, exist_ok=True)
os.makedirs(ESTIMATE_PATH, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

# Create Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Extract information from PDF
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
    except Exception as e:
        print(f"Error extracting info from {pdf_path}: {e}")
    return client_name, doc_number

# Sanitize filenames
def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename)

# Get a unique filename
def get_unique_filename(directory, filename):
    base, extension = os.path.splitext(filename)
    counter = 1
    unique_filename = filename

    while os.path.exists(os.path.join(directory, unique_filename)):
        unique_filename = f"{base} ({counter}){extension}"
        counter += 1

    return unique_filename

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
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

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

            client_name, doc_number = extract_info(file_path, keyword_client, keyword_number)
            if client_name and doc_number:
                new_filename = sanitize_filename(f"{client_name} {doc_number}.pdf")
                new_filename = get_unique_filename(target_folder, new_filename)  # Get unique filename
                new_file_path = os.path.join(target_folder, new_filename)
                os.rename(file_path, new_file_path)
                flash(f"File uploaded and renamed to {new_filename} in {target_folder}", 'success')
                return redirect(url_for('upload_file'))
            else:
                flash("Could not extract necessary information from the file", 'danger')
                return redirect(request.url)

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
