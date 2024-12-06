import struct

class BTree:
    BLOCK_SIZE = 512
    HEADER_SIZE = 512
    NODE_HEADER_SIZE = 24
    DEGREE = 10  

    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename, 'r+b')
        self.root_id = 0
        self.next_block_id = 1
        self._read_header()

    def _read_header(self):
        self.file.seek(0)
        header = self.file.read(self.HEADER_SIZE)
        self.root_id, self.next_block_id = struct.unpack(">QQ", header[8:24])

    def _write_header(self):
        self.file.seek(0)
        self.file.write(b"4337PRJ3")  
        self.file.write(struct.pack(">QQ", self.root_id, self.next_block_id))
        self.file.write(b'\x00' * (self.HEADER_SIZE - 24))  

    def insert(self, key, value):
        if self.root_id == 0:
            self.root_id = self.next_block_id
            self.next_block_id += 1
            root = self._create_node(is_root=True)
            root['keys'].append(key)
            root['values'].append(value)
            self._write_node(root)
            self._write_header()
        else:
            self._insert_into_node(self.root_id, key, value)

    def _create_node(self, is_root=False):
        return {
            'id': self.next_block_id,
            'parent_id': 0 if is_root else None,
            'keys': [],
            'values': [],
            'children': [0] * (self.DEGREE * 2),
        }

    def _insert_into_node(self, node_id, key, value):
        node = self._read_node(node_id)

        i = 0
        while i < len(node['keys']) and key > node['keys'][i]:
            i += 1

        if i < len(node['keys']) and key == node['keys'][i]:
            print(f"Error: Key {key} already exists.")
            return

        if node['children'][i] == 0:
            node['keys'].insert(i, key)
            node['values'].insert(i, value)
            if len(node['keys']) >= self.DEGREE * 2 - 1:
                self._split_node(node)
            else:
                self._write_node(node)
        else:
            self._insert_into_node(node['children'][i], key, value)

    def _split_node(self, node):
        mid_index = len(node['keys']) // 2
        mid_key = node['keys'][mid_index]
        mid_value = node['values'][mid_index]

        sibling = self._create_node()
        sibling['keys'] = node['keys'][mid_index + 1:]
        sibling['values'] = node['values'][mid_index + 1:]
        sibling['children'] = node['children'][mid_index + 1:]

        node['keys'] = node['keys'][:mid_index]
        node['values'] = node['values'][:mid_index]
        node['children'] = node['children'][:mid_index + 1]

        if node['parent_id'] == 0:
            new_root = self._create_node(is_root=True)
            new_root['keys'] = [mid_key]
            new_root['values'] = [mid_value]
            new_root['children'] = [node['id'], sibling['id']]
            self.root_id = new_root['id']
            node['parent_id'] = new_root['id']
            sibling['parent_id'] = new_root['id']
            self._write_node(new_root)
        else:
            parent = self._read_node(node['parent_id'])
            insert_index = parent['keys'].index(mid_key) if mid_key in parent['keys'] else len(parent['keys'])
            parent['keys'].insert(insert_index, mid_key)
            parent['values'].insert(insert_index, mid_value)
            parent['children'][insert_index + 1] = sibling['id']
            self._write_node(parent)

        self._write_node(node)
        self._write_node(sibling)
        self._write_header()

    def _read_node(self, block_id):
        self.file.seek(block_id * self.BLOCK_SIZE)
        data = self.file.read(self.BLOCK_SIZE)

        if len(data) < self.BLOCK_SIZE:
            data = data.ljust(self.BLOCK_SIZE, b'\x00')

        node = {
            'id': struct.unpack(">Q", data[0:8])[0],
            'parent_id': struct.unpack(">Q", data[8:16])[0],
            'keys': list(struct.unpack(">19Q", data[24:176])),
            'values': list(struct.unpack(">19Q", data[176:328])),
            'children': list(struct.unpack(">20Q", data[328:488])),
        }
        return node


    def _write_node(self, node):
        padded_keys = node['keys'] + [0] * (19 - len(node['keys']))
        padded_values = node['values'] + [0] * (19 - len(node['values']))
        padded_children = node['children'] + [0] * (20 - len(node['children']))

        data = struct.pack(">QQ", node['id'], node['parent_id'])
        data += struct.pack(">19Q", *padded_keys)
        data += struct.pack(">19Q", *padded_values)
        data += struct.pack(">20Q", *padded_children)

        data = data.ljust(self.BLOCK_SIZE, b'\x00')

        self.file.seek(node['id'] * self.BLOCK_SIZE)
        self.file.write(data)

    def search(self, key):
        return self._search_in_node(self.root_id, key)

    def _search_in_node(self, node_id, key):
        if node_id == 0:
            return None 

        node = self._read_node(node_id)

        for i in range(len(node['keys'])):
            if node['keys'][i] == key:
                return node['values'][i]

        for i in range(len(node['keys'])):
            if key < node['keys'][i]:
                return self._search_in_node(node['children'][i], key)

        return self._search_in_node(node['children'][-1], key)




