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

    def main_screen(self):
        """Displays the main login/register screen."""
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(
            self.root,
            text="Welcome to OmDayal Group of Institutions Library Management System",
            font=("Arial", 20, "bold"),
            bg="#f0f8ff",
            #fg="#4682b4"
            fg="#942e2e"
        ).pack(pady=30)

        tk.Button(
            self.root,
            text="Register",
            command=self.register_screen,
            width=20,
            font=("Arial", 12, "bold"),
            #bg="#4682b4",
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
            #bg="#4682b4",
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
            #bg="#4682b4",
            fg="white",
            activebackground="#5a9bd5",
            activeforeground="white"
        ).pack(pady=10)

    def register_screen(self):
        """Displays the registration screen."""
        username = simpledialog.askstring("Register", "Enter a username:")
        if not username:
            return

        password = simpledialog.askstring("Register", "Enter a password:", show="*")
        confirm_password = simpledialog.askstring("Register", "Confirm password:", show="*")

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        hashed_password = hash_password(password)

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")

    def login_screen(self):
        """Displays the login screen."""
        username = simpledialog.askstring("Login", "Enter your username:")
        if not username:
            return

        password = simpledialog.askstring("Login", "Enter your password:", show="*")
        hashed_password = hash_password(password)

        cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, hashed_password))
        user = cursor.fetchone()
        if user:
            self.user_id = user[0]
            messagebox.showinfo("Success", "Login successful!")
            self.library_screen()
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def library_screen(self):
        """Displays the main library management screen."""
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(
            self.root,
            text="OmDayal Group of Institutions Library Management System",
            font=("Arial", 20, "bold"),
            bg="#f0f8ff",
            #fg="#4682b4"
            fg="#942e2e"
        ).pack(pady=20)

        buttons = [
            ("Display Books", self.display_books),
            ("Borrow a Book", self.borrow_book_screen),
            ("Return a Book", self.return_book_screen),
            ("Add a Book", self.add_book_screen),
            ("Delete a Book", self.delete_book_screen),
            ("Logout", self.main_screen)
        ]

        for text, command in buttons:
            tk.Button(
                self.root,
                text=text,
                command=command,
                width=30,
                font=("Arial", 12, "bold"),
                #bg="#4682b4",
                bg="#942e2e",
                fg="white",
                activebackground="#5a9bd5",
                activeforeground="white"
            ).pack(pady=5)

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
        """Handles adding a new book."""
        title = simpledialog.askstring("Add Book", "Enter the book title:")
        author = simpledialog.askstring("Add Book", "Enter the author's name:")
        price = simpledialog.askfloat("Add Book", "Enter the book price:")
        available_copies = simpledialog.askinteger("Add Book", "Enter the number of available copies:")
        category = simpledialog.askstring("Add Book", "Enter the book category:")
        publisher = simpledialog.askstring("Add Book", "Enter the publisher's name:")

        cursor.execute("INSERT INTO book (title, author, price, available_copies, category, publisher) VALUES (?, ?, ?, ?, ?, ?)",
                       (title, author, price, available_copies, category, publisher))
        conn.commit()
        messagebox.showinfo("Success", f"Book '{title}' added successfully!")

    def delete_book_screen(self):
        """Handles deleting a book."""
        identifier = simpledialog.askstring("Delete Book", "Enter the book ID or Title:")
        if not identifier:
            return
        self.delete_book(identifier)

    def delete_book(self, identifier):
        """Processes the deletion of a book."""
        cursor.execute("SELECT id, title FROM book WHERE id = ? OR title = ?", (identifier, identifier))
        result = cursor.fetchone()

        if result:
            book_id, title = result
            cursor.execute("DELETE FROM book WHERE id = ?", (book_id,))
            conn.commit()
            messagebox.showinfo("Success", f"Book '{title}' deleted successfully!")
        else:
            messagebox.showerror("Error", "Book not found.")


if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()
