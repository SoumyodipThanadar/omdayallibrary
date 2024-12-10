import sqlite3
from datetime import datetime
import hashlib

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

def register():
    """Register a new user."""
    username = input("Enter a username: ")
    password = input("Enter a password: ")
    confirm_password = input("Confirm password: ")

    if password != confirm_password:
        print("Passwords do not match!")
        return False
    
    hashed_password = hash_password(password)

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        print("Registration successful!")
        return True
    except sqlite3.IntegrityError:
        print("Username already exists. Try again.")
        return False

def login():
    """Login an existing user."""
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    hashed_password = hash_password(password)

    cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = cursor.fetchone()
    if user:
        print("Login successful!")
        return user[0]  # Return user ID
    else:
        print("Invalid username or password.")
        return None

def borrow_book(user_id, identifier, search_by):
    """Borrow a book."""
    # Fetch book details based on the search type
    if search_by == "title":
        cursor.execute("SELECT id, title, available_copies, price FROM book WHERE title = ?", (identifier,))
    elif search_by == "category":
        cursor.execute("SELECT id, title, available_copies, price FROM book WHERE category = ? AND available_copies > 0 LIMIT 1", (identifier,))
    elif search_by == "publisher":
        cursor.execute("SELECT id, title, available_copies, price FROM book WHERE publisher = ? AND available_copies > 0 LIMIT 1", (identifier,))
    else:
        cursor.execute("SELECT id, title, available_copies, price FROM book WHERE id = ?", (identifier,))
    
    result = cursor.fetchone()
    if result and result[2] > 0:
        book_id, title, available_copies, price = result
        # Update available_copies (decrease by 1)
        cursor.execute("UPDATE book SET available_copies = available_copies - 1 WHERE id = ?", (book_id,))
        # Insert into borrowed_books table with 'B' for borrow
        borrow_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO borrowed_books (user_id, book_id, borrow_return, date_time) VALUES (?, ?, ?, ?)", 
                       (user_id, book_id, 'B', borrow_date))
        conn.commit()
        print(f"Book borrowed successfully! You borrowed '{title}'. Cost: Rs. {price}.")
    else:
        print("Book is not available or does not exist.")

def return_book(user_id, identifier, search_by):
    """Return a book."""
    # Fetch book details based on the search type
    if search_by == "title":
        cursor.execute("SELECT id, title FROM book WHERE title = ?", (identifier,))
    elif search_by == "category":
        cursor.execute("SELECT id, title FROM book WHERE category = ?", (identifier,))
    elif search_by == "publisher":
        cursor.execute("SELECT id, title FROM book WHERE publisher = ?", (identifier,))
    else:
        cursor.execute("SELECT id, title FROM book WHERE id = ?", (identifier,))
    
    book_result = cursor.fetchone()
    if book_result:
        book_id, title = book_result
        # Check if the user has borrowed this book
        cursor.execute("SELECT id FROM borrowed_books WHERE user_id = ? AND book_id = ? AND borrow_return = 'B'", (user_id, book_id))
        borrow_record = cursor.fetchone()
        if borrow_record:
            # Update available_copies (increase by 1)
            cursor.execute("UPDATE book SET available_copies = available_copies + 1 WHERE id = ?", (book_id,))
            # Update borrow_return to 'R' and set the return date
            return_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO borrowed_books (user_id, book_id, borrow_return, date_time) VALUES (?, ?, ?, ?)", 
                           (user_id, book_id, 'R', return_date))
            conn.commit()
            print(f"Book returned successfully! You returned '{title}'.")
        else:
            print("No record of this book being borrowed by you.")
    else:
        print("Book does not exist.")

def display_books():
    """Display all books."""
    cursor.execute("SELECT * FROM book")
    books = cursor.fetchall()
    print("Available Books:")
    print("| ID | Title                               | Author                  | Price | Available Copies | Category  | Publisher |")
    print("-" * 100)
    for book in books:
        print(f"| {book[0]:<2} | {book[1]:<35} | {book[2]:<22} | {book[3]:<5} | {book[4]:<16} | {book[5]:<9} | {book[6]:<9} |")

def add_book():
    """Add a new book to the library."""
    title = input("Enter the title of the book: ")
    author = input("Enter the author's name: ")
    price = float(input("Enter the price of the book: "))
    available_copies = int(input("Enter the number of available copies: "))
    category = input("Enter the book category: ")
    publisher = input("Enter the publisher's name: ")

    cursor.execute(
        "INSERT INTO book (title, author, price, available_copies, category, publisher) VALUES (?, ?, ?, ?, ?, ?)",
        (title, author, price, available_copies, category, publisher)
    )
    conn.commit()
    print(f"Book '{title}' added successfully!")

def delete_book(identifier, search_by):
    """Delete a book from the library."""
    # Fetch book details based on the search type
    if search_by == "title":
        cursor.execute("SELECT id, title FROM book WHERE title = ?", (identifier,))
    elif search_by == "category":
        cursor.execute("SELECT id, title FROM book WHERE category = ?", (identifier,))
    elif search_by == "publisher":
        cursor.execute("SELECT id, title FROM book WHERE publisher = ?", (identifier,))
    else:
        cursor.execute("SELECT id, title FROM book WHERE id = ?", (identifier,))

    book_result = cursor.fetchone()
    if book_result:
        book_id, title = book_result
        # Delete the book from the database
        cursor.execute("DELETE FROM book WHERE id = ?", (book_id,))
        conn.commit()
        print(f"Book '{title}' deleted successfully!")
    else:
        print("Book not found.")

def main():
    user_id = None
    while not user_id:
        print("\nWelcome to OmDayal Library Management System")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            register()
        elif choice == "2":
            user_id = login()
        elif choice == "3":
            exit()
        else:
            print("Invalid choice. Please try again.")

    while True:
        print("\nLibrary Management System")
        print("1. Display Books")
        print("2. Borrow a Book")
        print("3. Return a Book")
        print("4. Add a Book")
        print("5. Delete a Book")
        print("6. Logout")
        choice = input("Enter your choice: ")
        if choice == "1":
            display_books()
        elif choice == "2":
            print("Borrow by: 1. ID  2. Title  3. Category  4. Publisher")
            method = input("Enter method (1/2/3/4): ")
            identifier = input("Enter the relevant information: ")
            search_by = ["id", "title", "category", "publisher"][int(method) - 1]
            borrow_book(user_id, identifier, search_by)
        elif choice == "3":
            print("Return by: 1. ID  2. Title  3. Category  4. Publisher")
            method = input("Enter method (1/2/3/4): ")
            identifier = input("Enter the relevant information: ")
            search_by = ["id", "title", "category", "publisher"][int(method) - 1]
            return_book(user_id, identifier, search_by)
        elif choice == "4":
            add_book()
        elif choice == "5":
            print("Delete by: 1. ID  2. Title  3. Category  4. Publisher")
            method = input("Enter method (1/2/3/4): ")
            identifier = input("Enter the relevant information: ")
            search_by = ["id", "title", "category", "publisher"][int(method) - 1]
            delete_book(identifier, search_by)
        elif choice == "6":
            print("Logging out...")
            user_id = None
        else:
            print("Invalid choice. Please try again.")

# Run the main function
if __name__ == "__main__":
    main()
