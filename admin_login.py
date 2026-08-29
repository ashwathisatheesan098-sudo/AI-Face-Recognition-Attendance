import getpass

USERNAME = "admin"
PASSWORD = "admin123"

print("================================")
print("   FACE RECOGNITION SYSTEM")
print("      ADMIN LOGIN")
print("================================")

username = input("Enter Username: ")
password = getpass.getpass("Enter Password: ")

if username == USERNAME and password == PASSWORD:
    print("\nLogin successful!")
    print("Welcome, Administrator.")

    # Open admin menu
    while True:
        print("\n========== ADMIN MENU ==========")
        print("1. Register Student")
        print("2. Capture Dataset")
        print("3. Face Recognition")
        print("4. Exit")
        print("================================")

        choice = input("Enter your choice: ")

        if choice == "1":
            from register_student import register_student
            register_student()
        elif choice == "2":
            print("\nUse the capture_faces.py file to capture the dataset.")

        elif choice == "3":
            print("\nStarting Face Recognition...")
            import os
            os.system("python recognize_face.py")

        elif choice == "4":
            print("Exiting system...")
            break

        else:
            print("Invalid choice.")

else:
    print("\nInvalid username or password.")