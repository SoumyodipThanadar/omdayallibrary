import sqlite3
from datetime import datetime
import hashlib
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

# Connect to the SQLite database
conn = sqlite3.connect('OmDayalLibrary1.db')
cursor = conn.cursor()

# Create necessary tables if they don't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    price REAL,
    available_copies INTEGER,
    category TEXT,
    publisher TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS borrowed_books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    book_id INTEGER,
    borrow_return TEXT,
    date_time TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (book_id) REFERENCES book(id)
)
''')
conn.commit()


def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OmDayal Library Management System")
        self.root.geometry("800x600")
        self.root.configure(bg="#2E6F40")  # Set background color
        self.user_id = None
        self.main_screen()

    def force_focus(self, dialog):
        """Ensure the dialog grabs focus."""
        dialog.grab_set()
        dialog.focus_force()

    def main_screen(self):
        """Displays the main login/register screen."""
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(
            self.root,
            text="Welcome to OmDayal Group of Institutions Library Management System",
            font=("Arial", 20, "bold"),
            bg="#f0f8ff",
            fg="#942e2e"
        ).pack(pady=30)

        tk.Button(
            self.root,
            text="Register",
            command=self.register_screen,
            width=20,
            font=("Arial", 12, "bold"),
            bg="#942e2e",
            fg="white",
            activebackground="#5a9bd5",
            activeforeground="white"
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="Login",
            command=self.login_screen,
            width=20,
            font=("Arial", 12, "bold"),
            bg="#942e2e",
            fg="white",
            activebackground="#5a9bd5",
            activeforeground="white"
        ).pack(pady=10)

        # Add About button
        tk.Button(
            self.root,
            text="Help & Support",
            command=self.about_screen,
            width=20,
            font=("Arial", 12, "bold"),
            bg="#942e2e",
            fg="white",
            activebackground="#5a9bd5",
            activeforeground="white"
        ).pack(pady=10)



        tk.Button(
            self.root,
            text="Exit",
            command=self.root.quit,
            width=20,
            font=("Arial", 12, "bold"),
            bg="#942e2e",
            fg="white",
            activebackground="#5a9bd5",
            activeforeground="white"
        ).pack(pady=10)

        

    def about_screen(self):
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Help & Support")
        dialog.geometry("1000x600")
        dialog.configure(bg="#a9c6e7")

        about_text = (
    "OmDayal Library Management System\n"
    "Developed by: Soumyodip Thanadar, Arpan Maity, Prasanta Adak and Md. Asif\n"
    "Version: 1.0\n"
    "This system efficiently manages library operations including books, users, and borrow/return records.\n"
    "\n"
    "Features:\n"
    "- Book Management: Add, update, and remove books from the library catalog.\n"
    "- User Management: Register, update, and manage user accounts.\n"
    "- Borrow/Return Records: Track books borrowed by users and their return dates.\n"
    "- Search Functionality: Easily search for books by title, author, publisher or category.\n"
    "- Updation: Updation in Borrow and Return Timings\n"
    "\n"
    "Help and Support:\n"
    "If you need assistance or encounter any issues while using the system, please follow the steps below:\n"
    "- For additional support, contact our support team at: support@omdayalibrary.com\n"
    "- You can also reach us via phone at: +91-7044485965 (Monday to Friday, 9 AM to 6 PM).\n"
    "\n"
    "We hope you enjoy using OmDayal Library Management System!"
)


        tk.Label(dialog, text="Help & Support", font=("Arial", 18, "bold"), bg="#f0f8ff", fg="#FF2B00").pack(pady=10)
        tk.Label(dialog, text=about_text, bg="#f0f8ff", font=("Arial", 12, "bold"), justify="left").pack(pady=10)

        tk.Button(dialog, text="Close", command=dialog.destroy, bg="#FF2B00", fg="white", font=("Arial", 12, "bold")).pack(pady=10)

        self.force_focus(dialog)

    def register_screen(self):
        """Displays the registration screen."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Register")
        dialog.geometry("400x300")
        dialog.configure(bg="#f0f8ff")

        def register_user():
            username = username_entry.get()
            password = password_entry.get()
            confirm_password = confirm_password_entry.get()

            if password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match!", parent=dialog)
                return

            hashed_password = hash_password(password)

            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
                conn.commit()
                messagebox.showinfo("Success", "Registration successful!", parent=dialog)
                dialog.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists.", parent=dialog)

        tk.Label(dialog, text="Register", font=("Arial", 18, "bold"), bg="#f0f8ff", fg="#FF2B00").pack(pady=10)
        tk.Label(dialog, text="Username:", bg="#f0f8ff").pack(pady=5)
        username_entry = tk.Entry(dialog, font=("Arial", 12))
        username_entry.pack(pady=5)
        tk.Label(dialog, text="Password:", bg="#f0f8ff").pack(pady=5)
        password_entry = tk.Entry(dialog, font=("Arial", 12), show="*")
        password_entry.pack(pady=5)
        tk.Label(dialog, text="Confirm Password:", bg="#f0f8ff").pack(pady=5)
        confirm_password_entry = tk.Entry(dialog, font=("Arial", 12), show="*")
        confirm_password_entry.pack(pady=5)
        tk.Button(dialog, text="Register", command=register_user, bg="#FF2B00", fg="white", font=("Arial", 12, "bold")).pack(pady=10)

        self.force_focus(dialog)

    def login_screen(self):
        """Displays the login screen."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Login")
        dialog.geometry("400x300")
        dialog.configure(bg="#f0f8ff")

        def login_user():
            username = username_entry.get()
            password = password_entry.get()
            hashed_password = hash_password(password)

            cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, hashed_password))
            user = cursor.fetchone()
            if user:
                self.user_id = user[0]
                messagebox.showinfo("Success", "Login successful!", parent=dialog)
                dialog.destroy()
                self.library_screen()
            else:
                messagebox.showerror("Error", "Invalid username or password.", parent=dialog)

        tk.Label(dialog, text="Login", font=("Arial", 18, "bold"), bg="#f0f8ff", fg="#FF2B00").pack(pady=10)
        tk.Label(dialog, text="Username:", bg="#f0f8ff").pack(pady=5)
        username_entry = tk.Entry(dialog, font=("Arial", 12))
        username_entry.pack(pady=5)
        tk.Label(dialog, text="Password:", bg="#f0f8ff").pack(pady=5)
        password_entry = tk.Entry(dialog, font=("Arial", 12), show="*")
        password_entry.pack(pady=5)
        tk.Button(dialog, text="Login", command=login_user, bg="#FF2B00", fg="white", font=("Arial", 12, "bold")).pack(pady=10)

        self.force_focus(dialog)

    def library_screen(self):
        """Displays the main library management screen."""
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(
            self.root,
            text="OmDayal Group of Institutions Library Management System",
            font=("Arial", 20, "bold"),
            bg="#f0f8ff",
            fg="#942e2e"
        ).pack(pady=20)

        buttons = [
            ("Display Books", self.display_books),
            ("Borrow a Book", self.borrow_book_screen),
            ("Return a Book", self.return_book_screen),
            ("Add a Book", self.add_book_screen),
            ("Delete a Book", self.delete_book_screen),
            ("Help & Support", self.about_screen),
            ("Logout", self.main_screen)
        ]

        for text, command in buttons:
            tk.Button(
                self.root,
                text=text,
                command=command,
                width=30,
                font=("Arial", 12, "bold"),
                bg="#942e2e",
                fg="white",
                activebackground="#5a9bd5",
                activeforeground="white"
            ).pack(pady=5)




    
    
    '''def display_books(self):
        """Displays all available books."""
        cursor.execute("SELECT * FROM book")
        books = cursor.fetchall()

        book_window = tk.Toplevel(self.root)
        book_window.title("Available Books")
        book_window.configure(bg="#f0f8ff")

        tree = ttk.Treeview(book_window, columns=("ID", "Title", "Author", "Price", "Available Copies", "Category", "Publisher"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Title", text="Title")
        tree.heading("Author", text="Author")
        tree.heading("Price", text="Price")
        tree.heading("Available Copies", text="Available Copies")
        tree.heading("Category", text="Category")
        tree.heading("Publisher", text="Publisher")

        for book in books:
            tree.insert("", "end", values=book)

        tree.pack(fill="both", expand=True)'''




    def display_books(self):
        """Displays all available books."""
        cursor.execute("SELECT * FROM book")
        books = cursor.fetchall()

        book_window = tk.Toplevel(self.root)
        book_window.title("Available Books")
        book_window.configure(bg="#f0f8ff")

        tree = ttk.Treeview(book_window, columns=("ID", "Title", "Author", "Price", "Available Copies", "Category", "Publisher"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Title", text="Title")
        tree.heading("Author", text="Author")
        tree.heading("Price", text="Price")
        tree.heading("Available Copies", text="Available Copies")
        tree.heading("Category", text="Category")
        tree.heading("Publisher", text="Publisher")

        for book in books:
            tree.insert("", "end", values=book)

        tree.pack(fill="both", expand=True)







    def borrow_book_screen(self):
        """Handles borrowing a book."""
        identifier = simpledialog.askstring("Borrow a Book", "Enter the book ID or Title or Category or Publisher:")
        if not identifier:
            return
        self.borrow_book(self.user_id, identifier)

    def borrow_book(self, user_id, identifier):
        """Processes the borrowing of a book."""
        cursor.execute("SELECT id, title, available_copies, category, publisher FROM book WHERE id = ? OR title = ? OR category = ? OR publisher = ?",
                       (identifier, identifier, identifier, identifier))
        result = cursor.fetchone()

        if result and result[2] > 0:
            book_id, title, available_copies, category, publisher = result
            cursor.execute("UPDATE book SET available_copies = available_copies - 1 WHERE id = ?", (book_id,))
            borrow_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO borrowed_books (user_id, book_id, borrow_return, date_time) VALUES (?, ?, ?, ?)",
                           (user_id, book_id, 'B', borrow_date))
            conn.commit()
            messagebox.showinfo("Success", f"You borrowed '{title}' (Category: {category}, Publisher: {publisher}).")
        else:
            messagebox.showerror("Error", "Book is not available or does not exist.")

    def return_book_screen(self):
        """Handles returning a book."""
        identifier = simpledialog.askstring("Return a Book", "Enter the book ID or Title or Category or Publisher:")
        if not identifier:
            return
        self.return_book(self.user_id, identifier)

    def return_book(self, user_id, identifier):
        """Processes the return of a book."""
        cursor.execute("SELECT id, title, category, publisher FROM book WHERE id = ? OR title = ? OR category = ? OR publisher = ?",
                       (identifier, identifier, identifier, identifier))
        result = cursor.fetchone()

        if result:
            book_id, title, category, publisher = result
            cursor.execute("SELECT id FROM borrowed_books WHERE user_id = ? AND book_id = ? AND borrow_return = 'B'",
                           (user_id, book_id))
            borrow_record = cursor.fetchone()

            if borrow_record:
                cursor.execute("UPDATE book SET available_copies = available_copies + 1 WHERE id = ?", (book_id,))
                return_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("INSERT INTO borrowed_books (user_id, book_id, borrow_return, date_time) VALUES (?, ?, ?, ?)",
                               (user_id, book_id, 'R', return_date))
                conn.commit()
                messagebox.showinfo("Success", f"You returned '{title}' (Category: {category}, Publisher: {publisher}).")
            else:
                messagebox.showerror("Error", "You have not borrowed this book.")
        else:
            messagebox.showerror("Error", "Book does not exist.")

    def add_book_screen(self):
        """Handles adding a new book to the library."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Book")
        dialog.geometry("500x800")
        dialog.configure(bg="#a9c6e7")

        # Input labels and entry fields
        tk.Label(dialog, text="Add New Book", font=("Arial", 18, "bold"), bg="#f0f8ff", fg="#FF2B00").pack(pady=10)

        # Dictionary to store input field variables
        fields = {
            "Title": tk.StringVar(),
            "Author": tk.StringVar(),
            "Price": tk.StringVar(),
            "Available Copies": tk.StringVar(),
            "Category": tk.StringVar(),
            "Publisher": tk.StringVar()
        }

        for label, var in fields.items():
            tk.Label(dialog, text=f"{label}:", bg="#f0f8ff", font=("Arial", 12)).pack(pady=5)
            tk.Entry(dialog, textvariable=var, font=("Arial", 12)).pack(pady=5)

        def submit_book():
            try:
                # Retrieve input values
                title = fields["Title"].get()
                author = fields["Author"].get()
                price = float(fields["Price"].get())
                available_copies = int(fields["Available Copies"].get())
                category = fields["Category"].get()
                publisher = fields["Publisher"].get()

                if not title or not author or not category or not publisher:
                    raise ValueError("All fields except Price and Available Copies must be filled!")

                # Insert the book into the database
                cursor.execute(
                    "INSERT INTO book (title, author, price, available_copies, category, publisher) VALUES (?, ?, ?, ?, ?, ?)",
                    (title, author, price, available_copies, category, publisher)
                )
                conn.commit()
                messagebox.showinfo("Success", f"Book '{title}' added successfully!", parent=dialog)
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Error", str(e), parent=dialog)
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error: {str(e)}", parent=dialog)

        # Submit button
        tk.Button(dialog, text="Add Book", command=submit_book, bg="#FF2B00", fg="white", font=("Arial", 12, "bold")).pack(pady=20)

        # Focus on the dialog and prevent interaction with the main window
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.focus()

    def delete_book_screen(self):
        """Handles deleting a book from the library."""
        identifier = simpledialog.askstring("Delete Book", "Enter the Book ID or Title to Delete:")
        if not identifier:
            return
        self.delete_book(identifier)

    def delete_book(self, identifier):
        """Deletes the specified book from the database."""
        cursor.execute("DELETE FROM book WHERE id = ? OR title = ?", (identifier, identifier))
        conn.commit()
        messagebox.showinfo("Success", f"Book '{identifier}' has been deleted.")


# Main tkinter loop
if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop() 

