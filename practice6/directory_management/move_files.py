#4
import os
src="C:\\Users\\noutshopkz\\OneDrive\\Documents\\PP2\\game\\practice6\\ers.txt"

dst = "C:\\Users\\noutshopkz\\OneDrive\\Documents\\PP2\\game\\ers_backup3.txt"

os.rename(src,dst) #Renaming a Directory or a File -> os.rename(old_name, new_name)


os.chdir("C:\\Users\\noutshopkz\\OneDrive\\Documents\\PP2\\game\\practice6")
print(os.rename("cool","cool2")) #Renaming a Directory or a File -> os.rename(old_name, new_name)