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



Development

Code Structure:
ContactManager: Backend class for managing contacts.
ContactManagerGUI: Tkinter-based GUI class.


Contributing: Fork the repository, make changes, and submit a pull request. Follow the coding style in the existing code.


License
This project is licensed under the MIT License. See the LICENSE file for details.
Contributing


Built with ❤️ by Mr Zohaib
