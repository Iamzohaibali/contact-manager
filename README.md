Contact Manager
A Python-based desktop application for managing contacts with a Tkinter GUI. Features include adding, updating, deleting, searching, and filtering contacts, with support for categories, notes, undo functionality, and CSV import/export.
Features

Add/Edit/Delete Contacts: Manage contacts with name, phone, email, category, and notes.
Search and Filter: Search by name, phone, email, category, or notes, and filter by category.
Undo Functionality: Revert the last action (add, update, delete, or import).
CSV Import/Export: Import contacts from or export to CSV files.
Backup and Restore: Automatic backups and manual restore of contact data.
Input Validation: Validates names, phone numbers (using phonenumbers), and emails (using email-validator).
Pagination and Sorting: Display contacts in a paginated, sortable table.

Prerequisites

Python 3.8 or higher
Git (for cloning the repository)
A desktop environment to run the Tkinter GUI

Installation

Clone the Repository:git clone https://github.com/your-username/contact-manager.git
cd contact-manager


Create a Virtual Environment (recommended):python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Dependencies:pip install -r requirements.txt


Run the Application:python contact_manager.py



Dependencies
Listed in requirements.txt:

phonenumbers
email-validator
(Tkinter is included in Python's standard library)

Usage

Launch the application using python contact_manager.py.
Select or create a contacts.json file to store contacts.
Use the GUI to:
Add a Contact: Fill in the name, phone, email, category, and notes, then click "Add Contact".
Edit a Contact: Select a contact from the table, modify fields, and click "Update Contact".
Delete a Contact: Select a contact and click "Delete Selected".
Search and Filter: Use the search bar and category filter to find contacts.
Undo Actions: Click "Undo Last Action" to revert changes.
Import/Export: Use "Import from CSV" or "Export to CSV" for bulk operations.
Restore Backup: Select a backup file to restore previous contact data.



Sample Data

A sample contacts.json and sample.csv are provided in the data/ folder for testing.
To use sample data, place these files in the same directory as contact_manager.py or select them via the file dialog.

Development

Code Structure:
ContactManager: Backend class for managing contacts.
ContactManagerGUI: Tkinter-based GUI class.


Testing: Unit tests are available in the tests/ folder (optional, see below).
Contributing: Fork the repository, make changes, and submit a pull request. Follow the coding style in the existing code.

Testing
To run unit tests (if included):
python -m unittest discover tests

License
This project is licensed under the MIT License. See the LICENSE file for details.
Contributing

Fork the repository.
Create a new branch (git checkout -b feature/your-feature).
Commit your changes (git commit -m "Add your feature").
Push to the branch (git push origin feature/your-feature).
Open a pull request.

Contact
For issues or suggestions, open an issue on GitHub or contact [Your Name] via [Your Email or LinkedIn].

Built with ❤️ by [Your Name]
