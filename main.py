import os

def create_file(filename):
    if os.path.exists(filename):
        overwrite = input(f"File {filename} already exists. Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            print("Aborted.")
            return
    with open(filename, 'wb') as file:
        file.write(b"4337PRJ3" + b'\x00' * (512 - 8))  # Write magic number and fill remaining bytes
    print(f"Created file: {filename}")

def open_file(filename):
    if not os.path.exists(filename):
        print(f"File {filename} does not exist.")
        return None
    with open(filename, 'rb') as file:
        header = file.read(8)
        if header != b"4337PRJ3":
            print("Invalid file format.")
            return None
    print(f"Opened file: {filename}")
    return filename

def main():
    current_file = None
    while True:
        print("\nMenu:")
        print("1. Create")
        print("2. Open")
        print("3. Quit")
        choice = input("Enter your choice: ").strip().lower()

        if choice == "1" or choice == "create":
            filename = input("Enter filename to create: ").strip()
            create_file(filename)
        elif choice == "2" or choice == "open":
            filename = input("Enter filename to open: ").strip()
            current_file = open_file(filename)
        elif choice == "3" or choice == "quit":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
