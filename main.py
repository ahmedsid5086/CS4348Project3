import os
from btree import BTree

def create_file(filename):
    if os.path.exists(filename):
        overwrite = input(f"File {filename} already exists. Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            print("Aborted.")
            return
    with open(filename, 'wb') as file:
        file.write(b"4337PRJ3" + b'\x00' * (512 - 8)) 
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
    btree = None

    while True:
        print("\nMenu:")
        print("1. Create")
        print("2. Open")
        print("3. Insert")
        print("4. Search")
        print("5. Quit")
        choice = input("Enter your choice: ").strip().lower()

        if choice == "1" or choice == "create":
            filename = input("Enter filename to create: ").strip()
            create_file(filename)
        elif choice == "2" or choice == "open":
            filename = input("Enter filename to open: ").strip()
            current_file = open_file(filename)
            if current_file:
                btree = BTree(current_file) 
        elif choice == "3" or choice == "insert":
            if not btree:
                print("No file is currently open. Please open a file first.")
                continue
            try:
                key = int(input("Enter key (unsigned integer): ").strip())
                value = int(input("Enter value (unsigned integer): ").strip())
                if key < 0 or value < 0:
                    raise ValueError
                btree.insert(key, value)
            except ValueError:
                print("Invalid input. Please enter valid unsigned integers.")
        elif choice == "4" or choice == "search":
            if not btree:
                print("No file is currently open. Please open a file first.")
                continue
            try:
                key = int(input("Enter key to search for (unsigned integer): ").strip())
                if key < 0:
                    raise ValueError
                value = btree.search(key)
                if value is not None:
                    print(f"Key {key} found with value {value}.")
                else:
                    print(f"Key {key} not found.")
            except ValueError:
                print("Invalid input. Please enter a valid unsigned integer.")
        elif choice == "5" or choice == "quit":
            print("Goodbye!")
            break




if __name__ == "__main__":
    main()
