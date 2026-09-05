import tkinter as tk
from tkinter import messagebox

def login():
    username = username_entry.get()
    password = password_entry.get()

    if username == "admin" and password == "admin123":
        messagebox.showinfo("Login Successful", "Welcome!")
        root.destroy()

        # Open dashboard here later
        import dashboard
        dashboard.open_dashboard()

    else:
        messagebox.showerror("Login Failed", "Invalid username or password")


root = tk.Tk()
root.title("Face Recognition Attendance System")
root.geometry("400x300")

title_label = tk.Label(
    root,
    text="User Login",
    font=("Arial", 20, "bold")
)
title_label.pack(pady=25)

tk.Label(root, text="Username").pack()
username_entry = tk.Entry(root, width=30)
username_entry.pack(pady=5)

tk.Label(root, text="Password").pack()
password_entry = tk.Entry(root, width=30, show="*")
password_entry.pack(pady=5)

login_button = tk.Button(
    root,
    text="Login",
    width=15,
    command=login
)
login_button.pack(pady=20)

root.mainloop()