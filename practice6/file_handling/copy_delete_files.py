#4
import shutil

shutil.copy("ers.txt", "ers_backup.txt")

#5
import os

os.remove("ers.txt")