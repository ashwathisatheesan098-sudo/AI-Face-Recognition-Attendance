import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os


def run_module(filename):
    file_path = os.path.join(os.path.dirname(__file__), filename)

    if os.path.exists(file_path):
        subprocess.Popen([sys.executable, file_path])
    else:
        messagebox.showerror(
            "Error",
            f"{filename} was not found."
        )


def open_dashboard():

    dashboard = tk.Tk()
    dashboard.title("Admin Dashboard")
    dashboard.geometry("600x500")
    dashboard.resizable(False, False)

    # Title
    title = tk.Label(
        dashboard,
        text="Face Recognition Attendance System",
        font=("Arial", 20, "bold")
    )
    title.pack(pady=25)

    subtitle = tk.Label(
        dashboard,
        text="Admin Dashboard",
        font=("Arial", 15)
    )
    subtitle.pack(pady=5)

    # Register Student
    register_button = tk.Button(
        dashboard,
        text="Register Student",
        width=25,
        height=2,
        font=("Arial", 12),
        command=lambda: run_module("register_student.py")
    )
    register_button.pack(pady=10)


    # Build Embeddings
    embedding_button = tk.Button(
    dashboard,
    text="Build Face Embeddings",
    width=25,
    height=2,
    font=("Arial", 12),
    command=lambda: run_module("build_embeddings.py")
)

    # Start Recognition
    register_button = tk.Button(
    dashboard,
    text="Register Student",
    width=25,
    height=2,
    font=("Arial", 12),
    command=lambda: os.system("start http://127.0.0.1:5000/")
)

    # View Attendance
    attendance_button = tk.Button(
    dashboard,
    text="View Attendance",
    width=25,
    height=2,
    font=("Arial", 12),
    command=lambda: os.system("start http://127.0.0.1:5000/attendance")
)
    # Logout
    logout_button = tk.Button(
        dashboard,
        text="Logout",
        width=15,
        height=2,
        font=("Arial", 11),
        command=dashboard.destroy
    )
    logout_button.pack(pady=20)

    dashboard.mainloop()