import sqlite3
import hashlib
from datetime import datetime
import click
import shutil
from colorama import init, Fore
current_user_id = None
# Initialize colorama
init(autoreset=True)
def success_message(message):
    print(Fore.LIGHTGREEN_EX + message)

def error_message(message):
    print(Fore.LIGHTRED_EX + message)

def warn_message(message):
    print(Fore.YELLOW + message)

def exists_message(message):
    print(Fore.MAGENTA + message)
# Create the tables for users, transactions, and budgets
def create_tables():
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            type TEXT,
            category TEXT,
            date TEXT,
            description TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            user_id INTEGER,
            category TEXT,
            amount REAL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

# Hash password function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Register a new user
def register_user(username, password):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        success_message("User registered successfully!")
    except sqlite3.IntegrityError:
        exists_message("Username already exists!")
    conn.close()

# Login user
def login_user(username, password):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return user[0]  # Return user ID
    else:
        return None

# Add a transaction (income/expense)
def add_transaction(user_id, amount, trans_type, category, description=""):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO transactions (user_id, amount, type, category, date, description)
        VALUES (?, ?, ?, ?, ?, ?)''', (user_id, amount, trans_type, category, date, description))
    conn.commit()
    conn.close()

# Generate financial report
def generate_report(user_id, start_date, end_date):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT SUM(amount) FROM transactions
        WHERE user_id = ? AND type = 'income' AND date BETWEEN ? AND ?
    ''', (user_id, start_date, end_date))
    total_income = cursor.fetchone()[0] or 0

    cursor.execute('''
        SELECT SUM(amount) FROM transactions
        WHERE user_id = ? AND type = 'expense' AND date BETWEEN ? AND ?
    ''', (user_id, start_date, end_date))
    total_expenses = cursor.fetchone()[0] or 0

    savings = total_income - total_expenses
    print(f"Income: {total_income}, Expenses: {total_expenses}, Savings: {savings}")
    conn.close()

# Click command-line interface
@click.group()
def cli():
    pass

# Register user command
@click.command()
@click.option('--username', prompt='Username', help='Username for registration')
@click.option('--password', prompt='Password', hide_input=True, help='Password for registration')
def register(username, password):
    register_user(username, password)

# Login user command
@click.command()
@click.option('--username', prompt='Username', help='Username for login')
@click.option('--password', prompt='Password', hide_input=True, help='Password for login')
def login(username, password):
    global current_user_id
    current_user_id = login_user(username, password)
    if current_user_id:
        success_message("Login successful.")
    else:
        print("Login failed. Invalid credentials.")

# Add transaction command
@click.command()
@click.option('--amount', prompt='Amount', type=float, help='Amount for the transaction')
@click.option('--trans_type', prompt='Type (income/expense)', type=click.Choice(['income', 'expense']), help='Transaction type')
@click.option('--category', prompt='Category', help='Category of the transaction')
@click.option('--description', prompt='Description', default='', help='Description of the transaction')
def add(amount, trans_type, category, description):
    if current_user_id:
        add_transaction(current_user_id, amount, trans_type, category, description)
        print(f"{trans_type.capitalize()} added successfully.")
    else:
        print("Please login first.")

# Generate report command
@click.command()
@click.option('--start_date', prompt='Start date (YYYY-MM-DD)', help='Start date for the report')
@click.option('--end_date', prompt='End date (YYYY-MM-DD)', help='End date for the report')
def report(start_date, end_date):
    global current_user_id
    print(f"Debug: current_user_id = {current_user_id}")
    if current_user_id:
        generate_report(current_user_id, start_date, end_date)
    else:
        print("Please login first.")

# Add commands to CLI
cli.add_command(register)
cli.add_command(login)
cli.add_command(add)
cli.add_command(report)

if __name__ == '__main__':
    create_tables()  # Ensure tables are created
    current_user_id = None
    cli()
