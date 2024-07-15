# File Renamer

This project monitors specified directories for new PDF files and renames them based on extracted information from the files. It is designed to handle invoices and estimates, extracting client names and document numbers to create meaningful filenames.

## Features

- Monitors specified directories for new PDF files.
- Extracts client names and document numbers from the PDFs.
- Renames files based on the extracted information.
- Supports both invoices and estimates.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/muhindi-brian/File-Renamer.git
    cd File-Renamer
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Update the directory paths in `main.py` to point to your invoice and estimate directories:
    ```python
    invoice_path = r"your_invoice_directory_path"
    estimate_path = r"your_estimate_directory_path"
    ```

2. Run the script:
    ```sh
    python main.py
    ```

## Notes

- Ensure that the specified directories exist.
- The script will continuously monitor the directories for new PDF files.
- It will rename the files based on the extracted client names and document numbers.

## Contributing

If you find any issues or have suggestions for improvements, please feel free to create a pull request or open an issue.

## License

This project is licensed under the MIT License.
