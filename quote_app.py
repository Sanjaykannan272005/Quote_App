import tkinter as tk
from tkinter import messagebox
import sqlite3
import requests

# Database setup
def initialize_db():
    conn = sqlite3.connect("quotes_app.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        quote TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    conn.commit()
    conn.close()

# Fetch random quote from the API
def fetch_quote():
    try:
        response = requests.get("https://zenquotes.io/api/random", timeout=5)
        if response.status_code == 200:
            return f'"{response.json()[0]["q"]}" - {response.json()[0]["a"]}'
    except:
        messagebox.showerror("Error", "API request failed.")
    return None

# Main application window
def main_app(user_id):
    def generate_quote():
        quote = fetch_quote()
        if quote:
            quote_label.config(text=quote)

    def save_favorite():
        quote = quote_label.cget("text")
        if quote:
            conn = sqlite3.connect("quotes_app.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO favorites (user_id, quote) VALUES (?, ?)", (user_id, quote))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Quote added to favorites!")

    def show_favorites():
        conn = sqlite3.connect("quotes_app.db")
        cursor = conn.cursor()
        cursor.execute("SELECT quote FROM favorites WHERE user_id = ?", (user_id,))
        quotes = cursor.fetchall()
        conn.close()

        if quotes:
            win = tk.Toplevel(root)
            win.title("Favorites")
            win.geometry("400x300")
            for quote in quotes:
                tk.Label(win, text=quote[0], wraplength=350, font=("Arial", 12), justify="left").pack(pady=5)
        else:
            messagebox.showinfo("Info", "No favorites yet!")

    def clear_quote():
        quote_label.config(text="Click below to generate a quote!")

    root = tk.Tk()
    root.title("Quote Generator")
    root.geometry("500x500")
    root.config(bg="#f0f0f0")

    quote_frame = tk.Frame(root, bg="#f0f0f0")
    quote_frame.pack(pady=40)

    quote_label = tk.Label(quote_frame, text="Click to get a quote!", font=("Arial", 16, "bold"), bg="#f0f0f0", wraplength=400)
    quote_label.pack(pady=20)

    tk.Button(quote_frame, text="Generate Quote", command=generate_quote, width=20, height=2, bg="#4CAF50", fg="white", font=("Arial", 12), bd=0, relief="flat").pack(pady=10)
    tk.Button(quote_frame, text="Save to Favorites", command=save_favorite, width=20, height=2, bg="#2196F3", fg="white", font=("Arial", 12), bd=0, relief="flat").pack(pady=10)
    tk.Button(quote_frame, text="View Favorites", command=show_favorites, width=20, height=2, bg="#FF9800", fg="white", font=("Arial", 12), bd=0, relief="flat").pack(pady=10)
    tk.Button(quote_frame, text="Clear Quote", command=clear_quote, width=20, height=2, bg="#F44336", fg="white", font=("Arial", 12), bd=0, relief="flat").pack(pady=10)

    root.mainloop()

# Login and Registration
def login():
    username = username_entry.get()
    password = password_entry.get()

    conn = sqlite3.connect("quotes_app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        login_window.destroy()
        main_app(user[0])
    else:
        messagebox.showerror("Error", "Invalid credentials!")

def register():
    username = username_entry.get()
    password = password_entry.get()

    conn = sqlite3.connect("quotes_app.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Registration successful! Please log in.")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists!")

# Login window
initialize_db()

login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("300x400")

tk.Label(login_window, text="Username", font=("Arial", 12)).pack(pady=10)
username_entry = tk.Entry(login_window, font=("Arial", 12))
username_entry.pack(pady=5)

tk.Label(login_window, text="Password", font=("Arial", 12)).pack(pady=10)
password_entry = tk.Entry(login_window, font=("Arial", 12), show="*")
password_entry.pack(pady=5)

tk.Button(login_window, text="Login", command=login, width=15, height=2, bg="#4CAF50", fg="white", font=("Arial", 12)).pack(pady=20)
tk.Button(login_window, text="Register", command=register, width=15, height=2, bg="#2196F3", fg="white", font=("Arial", 12)).pack(pady=10)

login_window.mainloop()
