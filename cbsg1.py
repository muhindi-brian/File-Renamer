import os
import time
import pdfplumber
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

class InvoiceRenamerHandler(FileSystemEventHandler):
    def __init__(self, keyword, path):
        self.keyword = keyword
        self.path = path

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
            # Extract customer name and invoice number from the PDF
            customer_name, invoice_number, invoice_date = self.extract_info(event.src_path)
            if not customer_name or not invoice_number or not invoice_date:
                print(f"Could not extract necessary information from {filename}")
                return

            new_filename = f"{customer_name} {invoice_number} ({invoice_date}).pdf"
            new_filepath = os.path.join(directory, new_filename)
            os.rename(event.src_path, new_filepath)
            print(f"Renamed: {event.src_path} to {new_filepath}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    def extract_info(self, pdf_path):
        customer_name = None
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
                                customer_name = lines[i + 1].strip()
                            if self.keyword in line:
                                invoice_number = line.split(self.keyword)[-1].strip()
                            if 'Invoice Date' in line:
                                invoice_date = line.split('Invoice Date')[-1].strip()
                                # Assuming the date is in a recognizable format
                                invoice_date = datetime.strptime(invoice_date, '%d/%m/%Y').strftime('%d/%m/%y')
        except Exception as e:
            print(f"Error extracting info from {pdf_path}: {e}")
        return customer_name, invoice_number, invoice_date

if __name__ == "__main__":
    # Paths for invoices and proforma invoices
    invoice_path = r"C:\Users\brian\OneDrive\Desktop\MOJOKDEVKE\CBSG-ERP\INVOICES"
    pfi_path = r"C:\Users\brian\OneDrive\Desktop\MOJOKDEVKE\CBSG-ERP\PFI"

    # Create handlers for both invoice types
    invoice_handler = InvoiceRenamerHandler('Invoice #', invoice_path)
    pfi_handler = InvoiceRenamerHandler('Proforma Invoice #', pfi_path)

    # Set up observers for both directories
    observers = []
    for handler in [invoice_handler, pfi_handler]:
        observer = Observer()
        observer.schedule(handler, handler.path, recursive=False)
        observers.append(observer)
        observer.start()
        print(f"Monitoring directory: {handler.path}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for observer in observers:
            observer.stop()
        for observer in observers:
            observer.join()
