import os
import re  # Importing the re module for regular expressions
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import pdfplumber

# Configure paths
INVOICE_PATH = r"C:\Users\brian\OneDrive\Desktop\MOJOKDEVKE\INVOICES"
ESTIMATE_PATH = r"C:\Users\brian\OneDrive\Desktop\MOJOKDEVKE\ESTIMATES"

# Ensure directories exist
os.makedirs(INVOICE_PATH, exist_ok=True)
os.makedirs(ESTIMATE_PATH, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

# Create Flask app
app = Flask(__name__)
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

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # If user does not select file, browser may submit an empty part without filename
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Determine if the file is an invoice or an estimate
            if 'INV-' in filename:
                keyword_client = 'Bill To'
                keyword_number = 'Invoice#'
                target_folder = INVOICE_PATH
            elif 'EST-' in filename:
                keyword_client = 'Bill To'
                keyword_number = '# EST-'
                target_folder = ESTIMATE_PATH
            else:
                return "Unknown document type", 400

            # Extract information and rename file
            client_name, doc_number = extract_info(file_path, keyword_client, keyword_number)
            if client_name and doc_number:
                new_filename = sanitize_filename(f"{client_name} {doc_number}.pdf")
                new_file_path = os.path.join(target_folder, new_filename)
                os.rename(file_path, new_file_path)
                return f"File uploaded and renamed to {new_filename} in {target_folder}", 200
            else:
                return "Could not extract necessary information from the file", 400

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
