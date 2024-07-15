import os
import time
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
        
        # Check if the file is a PDF and not already renamed
        if not filename.lower().endswith(".pdf") or '_' not in filename:
            return
        
        # Assuming the original filename format is "ClientName_InvoiceNumber.pdf"
        try:
            client_name, invoice_number = filename.rsplit('_', 1)
            invoice_number, file_extension = os.path.splitext(invoice_number)
            new_filename = f"{client_name} {invoice_number}{file_extension}"
            new_filepath = os.path.join(directory, new_filename)
            os.rename(event.src_path, new_filepath)
            print(f"Renamed: {event.src_path} to {new_filepath}")
        except ValueError:
            print(f"File {filename} does not match the expected format.")

if __name__ == "__main__":
    path = r"C:\Users\brian\OneDrive\Desktop\MOJOKDEVKE\INVOICES"
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
