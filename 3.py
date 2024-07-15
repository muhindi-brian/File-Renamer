import os
import time
import pdfplumber
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class InvoiceRenamerHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        self.process(event)

    def process(self, event):
        # Extract the directory and filename
        directory, filename = os.path.split(event.src_path)

        # Check if the file is a PDF and if it hasn't been renamed yet
        if not filename.lower().endswith(".pdf") or 'INV-' not in filename:
            return

        try:
            # Extract invoice number from the filename
            invoice_number = filename.split('INV-')[1].split('.')[0]
            
            # Extract client name from the PDF
            client_name = self.extract_client_name(event.src_path)
            if not client_name:
                print(f"Could not extract client name from {filename}")
                return

            new_filename = f"{client_name} {invoice_number}.pdf"
            new_filepath = os.path.join(directory, new_filename)
            os.rename(event.src_path, new_filepath)
            print(f"Renamed: {event.src_path} to {new_filepath}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    def extract_client_name(self, pdf_path):
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        lines = text.split('\n')
                        for i, line in enumerate(lines):
                            if 'Bill To' in line:
                                return lines[i + 1].strip()
        except Exception as e:
            print(f"Error extracting client name from {pdf_path}: {e}")
        return None

if __name__ == "__main__":
    path = r"C:\Users\brian\OneDrive\Desktop\MOJOK DEV KE. SOLUTIONS\INVOICES"
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
