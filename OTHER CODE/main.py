import os
import time
import re
import pdfplumber
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class PDFRenamerHandler(FileSystemEventHandler):
    def __init__(self, keyword_client, keyword_number):
        self.keyword_client = keyword_client
        self.keyword_number = keyword_number

    def on_created(self, event):
        if event.is_directory:
            return
        self.process(event)

    def process(self, event):
        # Extract the directory and filename
        directory, filename = os.path.split(event.src_path)

        # Check if the file is a PDF
        if not filename.lower().endswith(".pdf"):
            return

        try:
            # Extract client name and invoice/estimate number from the PDF
            client_name, doc_number = self.extract_info(event.src_path)
            if not client_name or not doc_number:
                print(f"Could not extract necessary information from {filename}")
                return

            new_filename = self.sanitize_filename(f"{client_name} {doc_number}.pdf")
            new_filepath = os.path.join(directory, new_filename)
            os.rename(event.src_path, new_filepath)
            print(f"Renamed: {event.src_path} to {new_filepath}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    def extract_info(self, pdf_path):
        client_name = None
        doc_number = None
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        lines = text.split('\n')
                        for i, line in enumerate(lines):
                            print(f"Line {i}: {line}")  # Debugging: print each line
                            if self.keyword_client in line:
                                client_name = lines[i + 1].strip()
                                print(f"Found client name: {client_name}")  # Debugging: print the client name
                            if self.keyword_number in line:
                                doc_number = line.split(self.keyword_number)[-1].strip()
                                print(f"Found document number: {doc_number}")  # Debugging: print the document number
        except Exception as e:
            print(f"Error extracting info from {pdf_path}: {e}")
        return client_name, doc_number

    def sanitize_filename(self, filename):
        # Remove or replace invalid characters for Windows filenames
        return re.sub(r'[<>:"/\\|?*]', '', filename)

def ensure_directory_exists(path):
    if not os.path.isdir(path):
        print(f"Directory does not exist: {path}")
        return False
    return True

if __name__ == "__main__":
    # Define paths
    invoice_path = r"C:\Users\brian\OneDrive\Desktop\MOJOKDEVKE\CBSG-ERP\INVOICES"
    estimate_path = r"C:\Users\brian\OneDrive\Desktop\MOJOKDEVKE\CBSG-ERP\PFI"

    # Check if directories exist
    if not ensure_directory_exists(invoice_path) or not ensure_directory_exists(estimate_path):
        print("One or more specified directories do not exist. Exiting.")
        exit(1)

    # Create handlers for invoices and estimates
    invoice_handler = PDFRenamerHandler('Bill To', 'Invoice#')
    estimate_handler = PDFRenamerHandler('Bill To', '# EST-')

    # Set up observers for the directories
    observer = Observer()
    observer.schedule(invoice_handler, invoice_path, recursive=False)
    observer.schedule(estimate_handler, estimate_path, recursive=False)

    # Start the observers
    observer.start()
    print(f"Monitoring directories: {invoice_path} and {estimate_path}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
