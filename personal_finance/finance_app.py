import sqlite3
import getpass
from datetime import datetime
'''import shutil
from colorama import init, Fore
def success_message(message):
    print(Fore.LIGHTGREEN_EX + message)

def error_message(message):
    print(Fore.LIGHTRED_EX + message)

def warn_message(message):
    print(Fore.YELLOW + message)

def exists_message(message):
    print(Fore.MAGENTA + message)'''
# Database setup
def setup_database():
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE,
                      password TEXT
                      )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      amount REAL,
                      category TEXT,
                      type TEXT,
                      date TEXT,
                      FOREIGN KEY(user_id) REFERENCES users(id)
                      )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS budgets (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      category TEXT,
                      amount REAL,
                      FOREIGN KEY(user_id) REFERENCES users(id)
                      )''')
    
    conn.commit()
    conn.close()

# User registration
def register():
    username = input("Enter a username: ")
    password = getpass.getpass("Enter a password: ")

    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        print("Registration successful!")
    except sqlite3.IntegrityError:
        print("Username already exists. Try another.")
    finally:
        conn.close()

# User login
def login():
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")

    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        print("Login successful!")
        return user[0]
    else:
        print("Invalid credentials.")
        return None

# Add transaction
def add_transaction(user_id):
    amount = float(input("Enter the amount: "))
    category = input("Enter the category (e.g., Food, Rent, Salary): ")
    transaction_type = input("Enter the type (income/expense): ").lower()
    date = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO transactions (user_id, amount, category, type, date) VALUES (?, ?, ?, ?, ?)",
                   (user_id, amount, category, transaction_type, date))
    conn.commit()
    conn.close()
    print("Transaction added successfully!")

# Generate financial report
def generate_report(user_id):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type = 'income'", (user_id,))
    total_income = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type = 'expense'", (user_id,))
    total_expenses = cursor.fetchone()[0] or 0

    savings = total_income - total_expenses

    print(f"Total Income: Rs.{total_income:.2f}")
    print(f"Total Expenses: Rs.{total_expenses:.2f}")
    print(f"Savings: Rs.{savings:.2f}")

    conn.close()

# Main menu
def main():
    setup_database()

    print("Welcome to the Personal Finance Manager")

    while True:
        print("\nMenu:")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            register()
        elif choice == '2':
            user_id = login()
            if user_id:
                while True:
                    print("\nUser Menu:")
                    print("1. Add Transaction")
                    print("2. Generate Report")
                    print("3. Logout")

                    user_choice = input("Enter your choice: ")

                    if user_choice == '1':
                        add_transaction(user_id)
                    elif user_choice == '2':
                        generate_report(user_id)
                    elif user_choice == '3':
                        break
                    else:
                        print("Invalid choice. Try again.")
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
