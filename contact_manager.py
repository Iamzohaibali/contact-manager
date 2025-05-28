import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
import uuid
import phonenumbers
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
import shutil
from collections import deque
import csv
import glob

class ContactManager:
    """
    A class to manage contacts with enhanced functionalities including unique IDs,
    undo support, categories, notes, and robust file handling.
    """
    def __init__(self, filename='contacts.json'):
        """
        Initializes the ContactManager instance.

        :param filename: Name of the JSON file for storing contacts.
        """
        self.filename = filename
        self.contacts = []
        self.undo_stack = deque(maxlen=10)  # Store up to 10 actions for undo
        self.categories = ['Work', 'Personal', 'Family', 'Other']  # Default categories
        self.load_contacts()

    def load_contacts(self):
        """
        Loads contacts from the JSON file, handling errors gracefully.

        :return: List of contacts or empty list if loading fails.
        """
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as file:
                    contacts = json.load(file)
                    if isinstance(contacts, list):
                        # Ensure each contact has required fields
                        for contact in contacts:
                            if 'id' not in contact:
                                contact['id'] = str(uuid.uuid4())
                            if 'category' not in contact:
                                contact['category'] = 'Other'
                            if 'notes' not in contact:
                                contact['notes'] = ''
                            if 'last_modified' not in contact:
                                contact['last_modified'] = datetime.now().isoformat()
                        self.contacts = contacts
                        return self.contacts
            except (json.JSONDecodeError, IOError) as e:
                messagebox.showwarning("Warning", f"Failed to load contacts: {str(e)}. Starting with empty list.")
        return []

    def save_contacts(self):
        """
        Saves contacts to the JSON file with backup.
        """
        try:
            # Create backup
            if os.path.exists(self.filename):
                backup_filename = f"{self.filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy(self.filename, backup_filename)
            with open(self.filename, 'w', encoding='utf-8') as file:
                json.dump(self.contacts, file, indent=4)
        except IOError as e:
            raise IOError(f"Failed to save contacts: {str(e)}")

    def validate_inputs(self, name, phone, email):
        """
        Validates contact inputs.

        :param name: Contact name.
        :param phone: Contact phone number.
        :param email: Contact email address.
        :return: Tuple of (is_valid, error_message).
        """
        name = name.strip()
        phone = phone.strip()
        email = email.strip()

        if not name:
            return False, "Name is required."
        if not re.match(r"^[A-Za-z\s]{1,100}$", name):
            return False, "Name can only contain letters and spaces (max 100 characters)."

        try:
            parsed_phone = phonenumbers.parse(phone, None)
            if not phonenumbers.is_valid_number(parsed_phone):
                return False, "Invalid phone number format (e.g., +1234567890)."
            phone = phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.E164)  # Normalize phone
        except phonenumbers.NumberParseException:
            return False, "Invalid phone number format."

        if email:
            try:
                validate_email(email, check_deliverability=False)
            except EmailNotValidError as e:
                return False, f"Invalid email format: {str(e)}"

        return True, ""

    def add_contact(self, name, phone, email, category='Other', notes=''):
        """
        Adds a new contact with a unique ID.

        :param name: Full name of the contact.
        :param phone: Phone number of the contact.
        :param email: Email address of the contact.
        :param category: Contact category.
        :param notes: Additional notes for the contact.
        :return: The added contact or None if duplicate.
        """
        contact = {
            'id': str(uuid.uuid4()),
            'name': name,
            'phone': phone,
            'email': email,
            'category': category,
            'notes': notes,
            'last_modified': datetime.now().isoformat()
        }
        if self.is_duplicate(name, phone, email):
            return None
        self.undo_stack.append(('add', contact.copy()))
        self.contacts.append(contact)
        self.save_contacts()
        return contact

    def update_contact(self, contact_id, name, phone, email, category, notes):
        """
        Updates a contact by ID.

        :param contact_id: Unique ID of the contact to update.
        :param name: New name.
        :param phone: New phone number.
        :param email: New email address.
        :param category: New category.
        :param notes: New notes.
        :return: Boolean indicating success.
        """
        for contact in self.contacts:
            if contact['id'] == contact_id:
                old_contact = contact.copy()
                contact['name'] = name
                contact['phone'] = phone
                contact['email'] = email
                contact['category'] = category
                contact['notes'] = notes
                contact['last_modified'] = datetime.now().isoformat()
                self.undo_stack.append(('update', old_contact, contact.copy()))
                self.save_contacts()
                return True
        return False

    def delete_contact(self, contact_id):
        """
        Deletes a contact by ID.

        :param contact_id: Unique ID of the contact to delete.
        :return: Boolean indicating success.
        """
        for contact in self.contacts:
            if contact['id'] == contact_id:
                self.undo_stack.append(('delete', contact.copy()))
                self.contacts.remove(contact)
                self.save_contacts()
                return True
        return False

    def undo(self):
        """
        Undoes the last action (add, update, or delete).

        :return: Boolean indicating if undo was successful.
        """
        if not self.undo_stack:
            return False
        action = self.undo_stack.pop()
        if action[0] == 'add':
            self.contacts = [c for c in self.contacts if c['id'] != action[1]['id']]
        elif action[0] == 'delete':
            self.contacts.append(action[1])
        elif action[0] == 'update':
            for contact in self.contacts:
                if contact['id'] == action[2]['id']:
                    contact.update(action[1])
        elif action[0] == 'import':
            imported_ids = [c['id'] for c in action[1]]
            self.contacts = [c for c in self.contacts if c['id'] not in imported_ids]
        self.save_contacts()
        return True

    def is_duplicate(self, name, phone, email):
        """
        Checks if a contact with the same name, phone, or email exists.

        :return: Boolean indicating if duplicate exists.
        """
        try:
            parsed_phone = phonenumbers.parse(phone, None)
            normalized_phone = phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            normalized_phone = phone  # Fallback if parsing fails

        for contact in self.contacts:
            if (contact['name'].lower() == name.lower() or
                contact['phone'] == normalized_phone or
                (email and contact['email'].lower() == email.lower())):
                return True
        return False

    def view_contacts(self):
        """
        Returns all contacts.

        :return: List of contacts.
        """
        return self.contacts

    def search_contacts(self, search_term, field='all'):
        """
        Searches contacts by term in specified field, including category and notes.

        :param search_term: Term to search for.
        :param field: Field to search ('name', 'phone', 'email', 'category', 'notes', or 'all').
        :return: List of matching contacts.
        """
        results = []
        search_term = search_term.lower()
        for contact in self.contacts:
            if field == 'all':
                if (search_term in contact['name'].lower() or
                    search_term in contact['phone'].lower() or
                    search_term in contact['email'].lower() or
                    search_term in contact['category'].lower() or
                    search_term in contact['notes'].lower()):
                    results.append(contact)
            elif search_term in contact[field].lower():
                results.append(contact)
        return results

    def filter_by_category(self, category):
        """
        Filters contacts by category.

        :param category: Category to filter by.
        :return: List of matching contacts.
        """
        if category == 'All':
            return self.contacts
        return [contact for contact in self.contacts if contact['category'] == category]

    def export_to_csv(self, csv_filename):
        """
        Exports contacts to a CSV file.

        :param csv_filename: Name of the CSV file.
        :return: Boolean indicating success.
        """
        try:
            with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['id', 'name', 'phone', 'email', 'category', 'notes', 'last_modified'])
                writer.writeheader()
                for contact in self.contacts:
                    writer.writerow(contact)
            return True
        except IOError as e:
            messagebox.showerror("Error", f"Failed to export contacts: {str(e)}")
            return False

    def import_from_csv(self, csv_filename):
        """
        Imports contacts from a CSV file.

        :param csv_filename: Name of the CSV file.
        :return: Boolean indicating success.
        """
        try:
            with open(csv_filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                imported_contacts = []
                for row in reader:
                    # Validate imported data
                    is_valid, error_message = self.validate_inputs(row['name'], row['phone'], row.get('email', ''))
                    if not is_valid:
                        messagebox.showwarning("Warning", f"Skipping invalid contact {row['name']}: {error_message}")
                        continue
                    if not self.is_duplicate(row['name'], row['phone'], row.get('email', '')):
                        contact = {
                            'id': row.get('id', str(uuid.uuid4())),
                            'name': row['name'],
                            'phone': row['phone'],
                            'email': row.get('email', ''),
                            'category': row.get('category', 'Other'),
                            'notes': row.get('notes', ''),
                            'last_modified': row.get('last_modified', datetime.now().isoformat())
                        }
                        imported_contacts.append(contact)
                if imported_contacts:
                    self.undo_stack.append(('import', imported_contacts.copy()))
                    self.contacts.extend(imported_contacts)
                    self.save_contacts()
                return True
        except IOError as e:
            messagebox.showerror("Error", f"Failed to import contacts: {str(e)}")
            return False

    def restore_backup(self, backup_filename):
        """
        Restores contacts from a backup file.

        :param backup_filename: Name of the backup file.
        :return: Boolean indicating success.
        """
        try:
            with open(backup_filename, 'r', encoding='utf-8') as file:
                contacts = json.load(file)
                if isinstance(contacts, list):
                    self.undo_stack.append(('restore', self.contacts.copy()))
                    self.contacts = contacts
                    self.save_contacts()
                    return True
            return False
        except (json.JSONDecodeError, IOError) as e:
            messagebox.showerror("Error", f"Failed to restore backup: {str(e)}")
            return False

class ContactManagerGUI:
    """
    A Tkinter-based GUI for ContactManager with advanced features.
    """
    def __init__(self, root):
        """
        Initializes the GUI.

        :param root: Tkinter root window.
        """
        self.root = root
        self.root.title("Advanced Contact Management System")
        self.root.geometry("900x750")
        self.root.configure(bg="#e8ecef")
        self.root.resizable(True, True)

        # Initialize ContactManager with user-selected file
        self.filename = None
        self.manager = None
        self.current_page = 1
        self.contacts_per_page = 20

        # Styling
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, font=("Arial", 10))
        self.style.configure("TLabel", background="#e8ecef", font=("Arial", 10))
        self.style.configure("Treeview", font=("Arial", 10))
        self.style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.root, textvariable=self.status_var, background="#d1d9e6", relief="sunken", anchor="w")
        self.status_label.grid(row=1, column=0, sticky="ew")

        # Initialize components
        self.select_file()
        self.create_input_fields()
        self.create_contact_table()
        self.create_search_bar()
        self.create_action_buttons()
        self.update_contact_table()

    def select_file(self):
        """
        Prompts user to select a JSON file for contacts.
        """
        self.filename = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Select Contacts File"
        )
        if not self.filename:
            self.filename = 'contacts.json'
        self.manager = ContactManager(self.filename)
        self.status_var.set(f"Using file: {self.filename}")

    def create_input_fields(self):
        """
        Creates input fields for adding/editing contacts, including category and notes.
        """
        input_frame = ttk.LabelFrame(self.main_frame, text="Manage Contact", padding="10")
        input_frame.grid(row=0, column=0, sticky="ew", pady=5)
        input_frame.columnconfigure(1, weight=1)

        # Name
        ttk.Label(input_frame, text="Name:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=5)
        self.name_entry = ttk.Entry(input_frame, width=35)
        self.name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.name_entry.insert(0, "Enter name")
        self.name_entry.bind("<FocusIn>", lambda e: self.name_entry.delete(0, tk.END) if self.name_entry.get() == "Enter name" else None)
        self.name_entry.bind("<KeyRelease>", lambda e: self.validate_input_length(self.name_entry, 100))
        self.name_entry.focus()

        # Phone
        ttk.Label(input_frame, text="Phone:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=5)
        self.phone_entry = ttk.Entry(input_frame, width=35)
        self.phone_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.phone_entry.insert(0, "Enter phone (e.g., +1234567890)")
        self.phone_entry.bind("<FocusIn>", lambda e: self.phone_entry.delete(0, tk.END) if self.phone_entry.get().startswith("Enter phone") else None)
        self.phone_entry.bind("<KeyRelease>", lambda e: self.validate_input_length(self.phone_entry, 20))

        # Email
        ttk.Label(input_frame, text="Email:", font=("Arial", 10)).grid(row=2, column=0, sticky="w", padx=5)
        self.email_entry = ttk.Entry(input_frame, width=35)
        self.email_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        self.email_entry.insert(0, "Enter email")
        self.email_entry.bind("<FocusIn>", lambda e: self.email_entry.delete(0, tk.END) if self.email_entry.get() == "Enter email" else None)
        self.email_entry.bind("<KeyRelease>", lambda e: self.validate_input_length(self.email_entry, 100))

        # Category
        ttk.Label(input_frame, text="Category:", font=("Arial", 10)).grid(row=3, column=0, sticky="w", padx=5)
        self.category_combobox = ttk.Combobox(input_frame, values=self.manager.categories, state="readonly")
        self.category_combobox.set("Other")
        self.category_combobox.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        # Notes
        ttk.Label(input_frame, text="Notes:", font=("Arial", 10)).grid(row=4, column=0, sticky="nw", padx=5)
        self.notes_text = tk.Text(input_frame, height=4, width=35)
        self.notes_text.grid(row=4, column=1, padx=5, pady=2, sticky="ew")
        self.notes_text.bind("<KeyRelease>", lambda e: self.validate_notes_length())

        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Add Contact", command=self.add_contact).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Update Contact", command=self.update_contact).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Clear Fields", command=self.clear_entries).grid(row=0, column=2, padx=5)

        # Accessibility: Set Tab order
        self.name_entry.lift()
        self.phone_entry.lift()
        self.email_entry.lift()
        self.category_combobox.lift()
        self.notes_text.lift()

    def create_contact_table(self):
        """
        Creates a sortable, paginated table for contacts with category and last modified.
        """
        table_frame = ttk.LabelFrame(self.main_frame, text="Contacts", padding="10")
        table_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Treeview
        self.tree = ttk.Treeview(table_frame, columns=("ID", "Name", "Phone", "Email", "Category", "Last Modified"), show="headings", height=12)
        self.tree.heading("ID", text="ID", command=lambda: self.sort_column("ID", False))
        self.tree.heading("Name", text="Name", command=lambda: self.sort_column("Name", False))
        self.tree.heading("Phone", text="Phone", command=lambda: self.sort_column("Phone", False))
        self.tree.heading("Email", text="Email", command=lambda: self.sort_column("Email", False))
        self.tree.heading("Category", text="Category", command=lambda: self.sort_column("Category", False))
        self.tree.heading("Last Modified", text="Last Modified", command=lambda: self.sort_column("Last Modified", False))
        self.tree.column("ID", width=0, stretch=False)  # Hidden ID column
        self.tree.column("Name", width=150)
        self.tree.column("Phone", width=120)
        self.tree.column("Email", width=200)
        self.tree.column("Category", width=100)
        self.tree.column("Last Modified", width=150)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.on_contact_select)
        self.tree.bind("<Double-1>", self.show_notes)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pagination controls
        pagination_frame = ttk.Frame(table_frame)
        pagination_frame.grid(row=1, column=0, sticky="ew", pady=5)
        ttk.Button(pagination_frame, text="Previous", command=self.prev_page).grid(row=0, column=0, padx=5)
        self.page_label = ttk.Label(pagination_frame, text="Page 1")
        self.page_label.grid(row=0, column=1, padx=5)
        ttk.Button(pagination_frame, text="Next", command=self.next_page).grid(row=0, column=2, padx=5)

    def create_search_bar(self):
        """
        Creates a search bar with field and category selection.
        """
        search_frame = ttk.LabelFrame(self.main_frame, text="Search & Filter Contacts", padding="10")
        search_frame.grid(row=2, column=0, sticky="ew", pady=5)
        search_frame.columnconfigure(0, weight=1)

        # Search field selection
        self.search_field = ttk.Combobox(search_frame, values=["All", "Name", "Phone", "Email", "Category", "Notes"], state="readonly")
        self.search_field.set("All")
        self.search_field.grid(row=0, column=0, padx=5, sticky="w")
        
        # Search entry
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.grid(row=0, column=1, padx=5, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.search_contacts)

        # Category filter
        ttk.Label(search_frame, text="Filter by Category:").grid(row=0, column=2, padx=5, sticky="w")
        self.category_filter = ttk.Combobox(search_frame, values=['All'] + self.manager.categories, state="readonly")
        self.category_filter.set("All")
        self.category_filter.grid(row=0, column=3, padx=5, sticky="w")
        self.category_filter.bind("<<ComboboxSelected>>", self.search_contacts)

        # Clear search
        ttk.Button(search_frame, text="Clear Search", command=self.clear_search).grid(row=0, column=4, padx=5)

    def create_action_buttons(self):
        """
        Creates action buttons including export, import, and restore.
        """
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=3, column=0, pady=10, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.columnconfigure(3, weight=1)
        button_frame.columnconfigure(4, weight=1)

        ttk.Button(button_frame, text="Delete Selected", command=self.delete_contact).grid(row=0, column=0, padx=5, sticky="e")
        ttk.Button(button_frame, text="Undo Last Action", command=self.undo_action).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Export to CSV", command=self.export_to_csv).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Import from CSV", command=self.import_from_csv).grid(row=0, column=3, padx=5)
        ttk.Button(button_frame, text="Restore Backup", command=self.restore_backup).grid(row=0, column=4, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.exit_app).grid(row=0, column=5, padx=5, sticky="w")

    def validate_input_length(self, entry, max_length):
        """
        Limits input length in entry fields.

        :param entry: Entry widget.
        :param max_length: Maximum allowed length.
        """
        if len(entry.get()) > max_length:
            entry.delete(max_length, tk.END)

    def validate_notes_length(self):
        """
        Limits notes text length.
        """
        notes = self.notes_text.get("1.0", tk.END).strip()
        if len(notes) > 500:
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert("1.0", notes[:500])

    def add_contact(self):
        """
        Adds a new contact with validation and duplicate check.
        """
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        category = self.category_combobox.get()
        notes = self.notes_text.get("1.0", tk.END).strip()

        is_valid, error_message = self.manager.validate_inputs(name, phone, email)
        if not is_valid:
            self.status_var.set(error_message)
            messagebox.showerror("Error", error_message)
            return

        if self.manager.is_duplicate(name, phone, email):
            if not messagebox.askyesno("Duplicate Detected", "A similar contact exists. Add anyway?"):
                self.status_var.set("Add contact cancelled.")
                return

        try:
            contact = self.manager.add_contact(name, phone, email, category, notes)
            if contact:
                self.status_var.set("Contact added successfully.")
                messagebox.showinfo("Success", "Contact added successfully.")
                self.clear_entries()
                self.update_contact_table()
            else:
                self.status_var.set("Duplicate contact detected.")
                messagebox.showwarning("Warning", "Duplicate contact not added.")
        except IOError as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to save contact: {str(e)}")

    def update_contact(self):
        """
        Updates a selected contact with validation.
        """
        selected_item = self.tree.selection()
        if not selected_item:
            self.status_var.set("Select a contact to update.")
            messagebox.showwarning("Warning", "Please select a contact to update.")
            return

        contact_id = self.tree.item(selected_item)["values"][0]
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        category = self.category_combobox.get()
        notes = self.notes_text.get("1.0", tk.END).strip()

        is_valid, error_message = self.manager.validate_inputs(name, phone, email)
        if not is_valid:
            self.status_var.set(error_message)
            messagebox.showerror("Error", error_message)
            return

        # Check for name conflict with other contacts
        for contact in self.manager.view_contacts():
            if contact['id'] != contact_id and contact['name'].lower() == name.lower():
                if not messagebox.askyesno("Name Conflict", f"A contact with name '{name}' exists. Update anyway?"):
                    self.status_var.set("Update cancelled.")
                    return

        try:
            if self.manager.update_contact(contact_id, name, phone, email, category, notes):
                self.status_var.set("Contact updated successfully.")
                messagebox.showinfo("Success", "Contact updated successfully.")
                self.clear_entries()
                self.update_contact_table()
            else:
                self.status_var.set("Contact not found.")
                messagebox.showerror("Error", "Contact not found.")
        except IOError as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to update contact: {str(e)}")

    def on_contact_select(self, event):
        """
        Populates input fields when a contact is selected.

        :param event: Treeview selection event.
        """
        selected_item = self.tree.selection()
        if selected_item:
            contact_id = self.tree.item(selected_item)["values"][0]
            for contact in self.manager.view_contacts():
                if contact['id'] == contact_id:
                    self.name_entry.delete(0, tk.END)
                    self.name_entry.insert(0, contact['name'])
                    self.phone_entry.delete(0, tk.END)
                    self.phone_entry.insert(0, contact['phone'])
                    self.email_entry.delete(0, tk.END)
                    self.email_entry.insert(0, contact['email'])
                    self.category_combobox.set(contact['category'])
                    self.notes_text.delete("1.0", tk.END)
                    self.notes_text.insert("1.0", contact['notes'])
                    self.status_var.set("Selected contact for editing.")
                    break

    def show_notes(self, event):
        """
        Shows full notes in a popup on double-click.

        :param event: Treeview double-click event.
        """
        selected_item = self.tree.selection()
        if selected_item:
            contact_id = self.tree.item(selected_item)["values"][0]
            for contact in self.manager.view_contacts():
                if contact['id'] == contact_id:
                    notes_window = tk.Toplevel(self.root)
                    notes_window.title("Contact Notes")
                    notes_window.geometry("400x300")
                    notes_text = tk.Text(notes_window, wrap="word", height=10)
                    notes_text.insert("1.0", contact['notes'])
                    notes_text.config(state="disabled")
                    notes_text.pack(padx=10, pady=10, fill="both", expand=True)
                    ttk.Button(notes_window, text="Close", command=notes_window.destroy).pack(pady=5)
                    break

    def sort_column(self, col, reverse):
        """
        Sorts the contact table by the specified column.

        :param col: Column to sort by.
        :param reverse: Boolean to reverse sort order.
        """
        def safe_datetime(value):
            try:
                return datetime.fromisoformat(value) if value else datetime.min
            except ValueError:
                return datetime.min

        contacts = [(self.tree.set(item, col), item) for item in self.tree.get_children()]
        if col == "Last Modified":
            contacts.sort(key=lambda x: safe_datetime(x[0]), reverse=reverse)
        else:
            contacts.sort(reverse=reverse)
        for index, (_, item) in enumerate(contacts):
            self.tree.move(item, '', index)
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def update_contact_table(self, contacts=None):
        """
        Updates the contact table with pagination.

        :param contacts: List of contacts to display (default: all contacts).
        """
        for item in self.tree.get_children():
            self.tree.delete(item)

        contacts = contacts if contacts is not None else self.manager.view_contacts()
        start = (self.current_page - 1) * self.contacts_per_page
        end = start + self.contacts_per_page
        for contact in contacts[start:end]:
            self.tree.insert("", "end", values=(
                contact['id'],
                contact['name'],
                contact['phone'],
                contact['email'],
                contact['category'],
                contact['last_modified']
            ))
        self.page_label.config(text=f"Page {self.current_page} of {max(1, (len(contacts) + self.contacts_per_page - 1) // self.contacts_per_page)}")

    def prev_page(self):
        """
        Navigates to the previous page of contacts.
        """
        if self.current_page > 1:
            self.current_page -= 1
            self.update_contact_table(self.get_filtered_contacts())
            self.status_var.set(f"Showing page {self.current_page}.")

    def next_page(self):
        """
        Navigates to the next page of contacts.
        """
        contacts = self.get_filtered_contacts()
        max_pages = (len(contacts) + self.contacts_per_page - 1) // self.contacts_per_page
        if self.current_page < max_pages:
            self.current_page += 1
            self.update_contact_table(self.get_filtered_contacts())
            self.status_var.set(f"Showing page {self.current_page}.")

    def get_filtered_contacts(self):
        """
        Returns filtered contacts based on search and category filter.
        """
        contacts = self.manager.filter_by_category(self.category_filter.get())
        search_term = self.search_entry.get().strip()
        if search_term:
            field = self.search_field.get().lower()
            contacts = self.manager.search_contacts(search_term, field if field != 'all' else 'all')
        return contacts

    def search_contacts(self, event=None):
        """
        Filters contacts based on search term and field.
        """
        self.current_page = 1
        self.update_contact_table(self.get_filtered_contacts())
        contacts = self.get_filtered_contacts()
        self.status_var.set(f"Found {len(contacts)} matching contact(s).")

    def clear_search(self):
        """
        Clears the search bar and resets the table.
        """
        self.search_entry.delete(0, tk.END)
        self.search_field.set("All")
        self.category_filter.set("All")
        self.current_page = 1
        self.update_contact_table()
        self.status_var.set("Search cleared.")

    def delete_contact(self):
        """
        Deletes the selected contact with confirmation.
        """
        selected_item = self.tree.selection()
        if not selected_item:
            self.status_var.set("Please select a contact to delete.")
            messagebox.showwarning("Warning", "Please select a contact to delete.")
            return

        contact_id = self.tree.item(selected_item)["values"][0]
        name = self.tree.item(selected_item)["values"][1]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {name}?"):
            try:
                if self.manager.delete_contact(contact_id):
                    self.status_var.set("Contact deleted successfully.")
                    messagebox.showinfo("Success", "Contact deleted successfully.")
                    self.clear_entries()
                    self.update_contact_table(self.get_filtered_contacts())
                else:
                    self.status_var.set("Contact not found.")
                    messagebox.showerror("Error", "Contact not found.")
            except IOError as e:
                self.status_var.set(f"Error: {str(e)}")
                messagebox.showerror("Error", f"Failed to delete contact: {str(e)}")

    def undo_action(self):
        """
        Undoes the last action.
        """
        if self.manager.undo():
            self.status_var.set("Last action undone.")
            messagebox.showinfo("Success", "Last action undone.")
            self.clear_entries()
            self.update_contact_table(self.get_filtered_contacts())
        else:
            self.status_var.set("No actions to undo.")
            messagebox.showwarning("Warning", "No actions to undo.")

    def export_to_csv(self):
        """
        Exports contacts to a CSV file.
        """
        csv_filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Contacts as CSV"
        )
        if csv_filename:
            if self.manager.export_to_csv(csv_filename):
                self.status_var.set("Contacts exported successfully.")
                messagebox.showinfo("Success", "Contacts exported successfully.")
            else:
                self.status_var.set("Export failed.")
                messagebox.showerror("Error", "Failed to export contacts.")

    def import_from_csv(self):
        """
        Imports contacts from a CSV file.
        """
        csv_filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Select CSV File to Import"
        )
        if csv_filename:
            if self.manager.import_from_csv(csv_filename):
                self.status_var.set("Contacts imported successfully.")
                messagebox.showinfo("Success", "Contacts imported successfully.")
                self.update_contact_table(self.get_filtered_contacts())
            else:
                self.status_var.set("Import failed.")
                messagebox.showerror("Error", "Failed to import contacts.")

    def restore_backup(self):
        """
        Restores contacts from a backup file.
        """
        backup_files = glob.glob(f"{self.filename}.backup_*")
        if not backup_files:
            self.status_var.set("No backup files found.")
            messagebox.showwarning("Warning", "No backup files found.")
            return

        backup_window = tk.Toplevel(self.root)
        backup_window.title("Restore Backup")
        backup_window.geometry("400x300")

        backup_listbox = tk.Listbox(backup_window, height=10)
        backup_listbox.pack(padx=10, pady=10, fill="both", expand=True)
        for backup in backup_files:
            backup_listbox.insert(tk.END, os.path.basename(backup))

        def restore_selected():
            selection = backup_listbox.curselection()
            if selection:
                backup_file = backup_files[selection[0]]
                if self.manager.restore_backup(backup_file):
                    self.status_var.set("Backup restored successfully.")
                    messagebox.showinfo("Success", "Backup restored successfully.")
                    self.update_contact_table(self.get_filtered_contacts())
                    backup_window.destroy()
                else:
                    self.status_var.set("Restore failed.")
                    messagebox.showerror("Error", "Failed to restore backup.")

        ttk.Button(backup_window, text="Restore Selected", command=restore_selected).pack(pady=5)
        ttk.Button(backup_window, text="Cancel", command=backup_window.destroy).pack(pady=5)

    def clear_entries(self):
        """
        Clears input fields and sets focus.
        """
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.category_combobox.set("Other")
        self.notes_text.delete("1.0", tk.END)
        self.name_entry.insert(0, "Enter name")
        self.phone_entry.insert(0, "Enter phone (e.g., +1234567890)")
        self.email_entry.insert(0, "Enter email")
        self.name_entry.focus()
        self.status_var.set("Fields cleared.")

    def exit_app(self):
        """
        Exits the application after confirmation.
        """
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.destroy()

def main():
    """
    Main function to launch the GUI application.
    """
    root = tk.Tk()
    app = ContactManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()