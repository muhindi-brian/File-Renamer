import os
import time
import pdfplumber
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

class InvoiceRenamerHandler(FileSystemEventHandler):
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
            # Extract client name, invoice number, and date from the PDF
            client_name, invoice_number, invoice_date = self.extract_info(event.src_path)
            if not client_name or not invoice_number or not invoice_date:
                print(f"Could not extract necessary information from {filename}")
                return

            new_filename = f"{client_name} {invoice_number} ({invoice_date}).pdf"
            new_filepath = os.path.join(directory, new_filename)
            os.rename(event.src_path, new_filepath)
            print(f"Renamed: {event.src_path} to {new_filepath}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    def extract_info(self, pdf_path):
        client_name = None
        invoice_number = None
        invoice_date = None
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        lines = text.split('\n')
                        for i, line in enumerate(lines):
                            if 'Bill To' in line:
                                client_name = lines[i + 1].strip()
                            if 'Invoice#' in line:
                                invoice_number = line.split('Invoice#')[-1].strip()
                            if 'Invoice Date' in line:
                                invoice_date = line.split('Invoice Date')[-1].strip()
                                # Assuming the date is in a recognizable format, convert to desired format
                                invoice_date = datetime.strptime(invoice_date, '%d/%m/%Y').strftime('%d/%m/%y')
        except Exception as e:
            print(f"Error extracting info from {pdf_path}: {e}")
        return client_name, invoice_number, invoice_date

if __name__ == "__main__":
    path = r"C:\Users\brian\OneDrive\Desktop\MOJOKDEVKE\INVOICES"
    print(f"Monitoring directory: {path}")  # Confirm the path is correct
    event_handler = InvoiceRenamerHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
