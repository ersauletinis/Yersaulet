import csv
from connect import ers

try:
    connec = ers()

    # 1 create table 
    with connec.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS phonebook(
                name VARCHAR(50) ,
                phone_number VARCHAR(20) NOT NULL);
        """)
        connec.commit()
        print("Table created")

    # 2 CSV file
    file_path="contacts.csv"
    with connec.cursor() as cursor:
        with open(file_path, mode='r') as f:
            reader=csv.reader(f)
            for row in reader:
                name=row[0]
                phone=row[1]

                cursor.execute(
                    """ INSERT INTO phonebook(name,phone_number)
                    VALUES (%s,%s)""",(name,phone)
                )
            connec.commit()
            print("CSV successful")

    # 3 inserting data entered from the console
    name=input("Enter your name: ")
    phone_number=input("Enter your phone number: ")

    with connec.cursor() as cursor:
        cursor.execute(
            """INSERT INTO phonebook(name,phone_number) 
            VALUES (%s,%s)""",(name,phone_number)
        )
        connec.commit()
        print(f"Contact {name} successfully added!")

    4 
    target_name=input("Enter the name of the contact you want to change: ")
    new_phone=input("Enter the new phone number: ")
    with connec.cursor() as cursor:
        cursor.execute(
            """ UPDATE phonebook SET phone_number= %s WHERE name = %s """
            ,(new_phone,target_name)
        )
        connec.commit()
        print("Data updated!")

    5

    search_term = input("Enter a name or beginning of a number to search: ")
    
    with connec.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM phonebook WHERE name ILIKE %s OR phone_number LIKE %s",
            (f'%{search_term}%', f'{search_term}%')
        )
        results = cursor.fetchall()
        for row in results:
            print(f"Name: {row[0]} | Phone: {row[1]}")

    #6 delete information in table 
    value=input()
    with connec.cursor() as cursor:
        cursor.execute(
            "DELETE FROM phonebook WHERE name = %s OR phone_number = %s",
            (value, value)
        )
        connec.commit()
        print("Contact was deleted")


except Exception as e:
    print("Error:", e)

finally:
    if connec:
        connec.close()
        print("Connection closed")