import struct
import os

BLOCK_SIZE = 512
MAGIC_NUMBER = b"4337PRJ3"
MAX_KEYS = 19
MAX_CHILDREN = 20


class BTreeNode:
    def __init__(self, block_id, is_leaf=True):
        self.block_id = block_id
        self.is_leaf = is_leaf
        self.keys = []
        self.values = []
        self.children = []
        self.parent_block_id = 0

    def to_bytes(self):
        block = struct.pack(">Q", self.block_id)
        block += struct.pack(">Q", self.parent_block_id)
        block += struct.pack(">Q", len(self.keys))
        block += b"".join(k.to_bytes(8, 'big') if k else (b"\x00" * 8) for k in self.keys)
        block += b"".join(v.to_bytes(8, 'big') if v else (b"\x00" * 8) for v in self.values)
        block += b"".join(c.to_bytes(8, 'big') if c else (b"\x00" * 8) for c in self.children)
        return block.ljust(BLOCK_SIZE, b"\x00")

    @classmethod
    def from_bytes(cls, data):
        block_id, parent_block_id, num_keys = struct.unpack(">QQQ", data[:24])
        keys = [int.from_bytes(data[24 + i * 8:32 + i * 8], 'big') for i in range(MAX_KEYS)]
        values = [int.from_bytes(data[176 + i * 8:184 + i * 8], 'big') for i in range(MAX_KEYS)]
        children = [int.from_bytes(data[328 + i * 8:336 + i * 8], 'big') for i in range(MAX_CHILDREN)]
        node = cls(block_id, is_leaf=(children[0] == 0))
        node.parent_block_id = parent_block_id
        node.keys = [k for k in keys if k != 0]
        node.values = [v for v in values if v != 0]
        node.children = [c for c in children if c != 0]
        return node


class BTree:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file = None
        self.root = None
        self.next_block_id = 1
        self.nodes_in_memory = {}

    def create(self, overwrite=False):
        if os.path.exists(self.file_path) and not overwrite:
            raise FileExistsError(f"File {self.file_path} already exists. Use overwrite to replace it.")
        self.file = open(self.file_path, "wb+")
        self.root = BTreeNode(0, True)
        self._write_header()
        self._flush_node(self.root)

    def open(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File {self.file_path} does not exist.")
        self.file = open(self.file_path, "rb+")
        if self.file.read(8) != MAGIC_NUMBER:
            raise ValueError("Invalid file format.")
        self.file.seek(0)
        self._read_header()
        self.root = self._read_node(0)

    def insert(self, key, value):
        if not self.root:
            raise RuntimeError("B-Tree is not initialized. Create or open a file first.")
        self._insert_into_node(self.root, key, value)

    def _insert_into_node(self, node, key, value):
        if node.is_leaf:
            if key in node.keys:
                raise ValueError(f"Key {key} already exists.")
            node.keys.append(key)
            node.values.append(value)
            node.keys.sort()
            self._flush_node(node)
        else:
            raise NotImplementedError("Splitting logic is not implemented.")

    def search(self, key):
        node = self.root
        while node:
            for i, k in enumerate(node.keys):
                if k == key:
                    return node.values[i]
                elif key < k:
                    node = self._read_node(node.children[i])
                    break
            else:
                node = self._read_node(node.children[-1])
        return None

    def print_tree(self):
        def print_node(node, level=0):
            print("  " * level + f"Node {node.block_id}: {node.keys}")
            for child_id in node.children:
                child = self._read_node(child_id)
                print_node(child, level + 1)
        print_node(self.root)

    def extract(self, output_file):
        with open(output_file, "w") as f:
            self._extract_node(self.root, f)

    def _extract_node(self, node, file):
        for key, value in zip(node.keys, node.values):
            file.write(f"{key},{value}\n")
        for child_id in node.children:
            child = self._read_node(child_id)
            self._extract_node(child, file)

    def _flush_node(self, node):
        self.file.seek((node.block_id + 1) * BLOCK_SIZE)
        self.file.write(node.to_bytes())
        if len(self.nodes_in_memory) > 3:
            block_id_to_evict = list(self.nodes_in_memory.keys())[0]
            del self.nodes_in_memory[block_id_to_evict]

    def _read_node(self, block_id):
        if block_id in self.nodes_in_memory:
            return self.nodes_in_memory[block_id]
        self.file.seek((block_id + 1) * BLOCK_SIZE)
        data = self.file.read(BLOCK_SIZE)
        node = BTreeNode.from_bytes(data)
        self.nodes_in_memory[block_id] = node
        return node

    def _write_header(self):
        header = MAGIC_NUMBER + struct.pack(">QQ", 0, self.next_block_id)
        header = header.ljust(BLOCK_SIZE, b"\x00")
        self.file.seek(0)
        self.file.write(header)

    def _read_header(self):
        self.file.seek(0)
        self.file.read(8)  # Skip magic number
        root_block_id, self.next_block_id = struct.unpack(">QQ", self.file.read(16))

    def close(self):
        if self.file:
            self.file.close()
            self.file = None


def interactive_menu():
    print("Welcome to the Complete B-Tree Index File Manager!")
    tree = None

    while True:
        print("\nCommands:")
        print("1. Create")
        print("2. Open")
        print("3. Insert")
        print("4. Search")
        print("5. Print")
        print("6. Extract")
        print("7. Load")
        print("8. Quit")
        choice = input("Enter your choice: ").strip().lower()

        try:
            if choice == "1" or choice == "create":
                file_path = input("Enter the file name to create: ").strip()
                if os.path.exists(file_path):
                    overwrite = input(f"File '{file_path}' exists. Overwrite? (yes/no): ").strip().lower()
                    if overwrite != "yes":
                        print("File creation aborted.")
                        continue
                tree = BTree(file_path)
                tree.create(overwrite=True)
                print(f"File '{file_path}' created successfully.")
            elif choice == "2" or choice == "open":
                file_path = input("Enter the file name to open: ").strip()
                tree = BTree(file_path)
                tree.open()
                print(f"File '{file_path}' opened successfully.")
            elif choice == "3" or choice == "insert":
                if tree:
                    key = int(input("Enter the key (unsigned integer): "))
                    value = int(input("Enter the value (unsigned integer): "))
                    tree.insert(key, value)
                    print(f"Inserted key {key} with value {value}.")
                else:
                    print("No file is open. Please create or open a file first.")
            elif choice == "4" or choice == "search":
                if tree:
                    key = int(input("Enter the key to search: "))
                    result = tree.search(key)
                    if result is not None:
                        print(f"Key found: Value = {result}")
                    else:
                        print("Key not found.")
                else:
                    print("No file is open. Please create or open a file first.")
            elif choice == "5" or choice == "print":
                if tree:
                    tree.print_tree()
                else:
                    print("No file is open. Please create or open a file first.")
            elif choice == "6" or choice == "extract":
                if tree:
                    output_file = input("Enter the output file name: ").strip()
                    tree.extract(output_file)
                    print(f"B-Tree contents extracted to {output_file}.")
                else:
                    print("No file is open. Please create or open a file first.")
            elif choice == "7" or choice == "load":
                if tree:
                    input_file = input("Enter the input file name: ").strip()
                    tree.load(input_file)
                    print(f"Loaded key-value pairs from {input_file}.")
                else:
                    print("No file is open. Please create or open a file first.")
            elif choice == "8" or choice == "quit":
                print("Exiting the program.")
                if tree:
                    tree.close()
                break
            else:
                print("Invalid choice. Please try again.")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    interactive_menu()
