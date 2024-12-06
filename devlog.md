## 12/5/2024 5:48 pm
## Thoughts So Far
I know this project involves building an interactive program to create and manage index files using a B-Tree structure. I am planning on creating this project using python for its simplicity and built-in big-endian support.

## Plan for This Session
- Initialize the Git repository.
- Create a basic project structure with placeholder files.
- Write the `create` and `open` commands as a starting point.
<<<<<<< HEAD

## 12/5/2024 6:26 pm
- Implemented and tested `create` and `open` commands.
- Learned how to handle binary file headers in Python.
- Next Steps: Implement `insert` and `search` commands.

## 12/5/2024 7:28 pm
- Successfully implemented the `insert` command, including handling node splits when the maximum degree was exceeded.
- Implemented the `search` command to traverse the B-Tree and return the value of a specified key.
- Tested both commands and confirmed they handle valid inputs and edge cases (e.g., duplicate keys, missing keys).
- Next Steps: Work on the `load` command to enable bulk insertion from a file.
## 12/5/2024 11:00 pm
- Successfully implemented the create and open commands, allowing users to initialize and access B-Tree index files with proper validation.
- Implemented the insert command, enabling key-value pair insertion with duplicate key detection.
- Added the search command, which traverses the B-Tree to find and return values for specified keys.
- Developed the print command to display all key-value pairs stored in the B-Tree.
- Implemented the extract command, enabling the export of all key-value pairs to an external file.
- Thoroughly tested all commands and confirmed functionality under various scenarios, including edge cases such as duplicate keys and invalid file formats.
