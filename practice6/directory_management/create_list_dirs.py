import os 
print(os.getcwd()) #cwd → current working director
#1
os.chdir("C:\\Users\\noutshopkz\\OneDrive\\Documents\\PP2\\game\\practice6")
os.makedirs("parent/child/grandchild")

#2
print(os.listdir()) # ['builtin_functions', 'directory_management', 'file_handling']

#3
for file in os.listdir("C:\\Users\\noutshopkz\\OneDrive\\Documents\\PP2\\game"):
    if(file.endswith(".txt")):
        print(file)

# os.chdir("C:\\Users\\noutshopkz\\OneDrive\\Documents\\PP2\\game\\practice6")
# print(os.mkdir()) #Making a new directory in Python










