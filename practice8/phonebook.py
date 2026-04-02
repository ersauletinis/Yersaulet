import csv
from connect1 import ers

try:
    connec = ers()
    # 1 Search by pattern
    a=input()
    with connec.cursor() as cursor:
        cursor.execute(
            'SELECT * FROM sa(%s)',(a,)
        )
        rows=cursor.fetchall()
        for i in rows:
            print(i, end=" ")
        connec.commit()

    
    # 2 Add user 
    #call era('Yersaulet','7777777')
    a=input("name: ")
    b=input("phone: ")
    with connec.cursor() as cursor:
        cursor.execute(
            'call era(%s,%s)',(a,b)
        )
        connec.commit()


    # 3 Array
    data=[]
    while True:
        name = input("Name: ")
        if name.lower() == "stop":
            break
        phone = input("Phone: ")
        data.append([name, phone])

    print("\nВводишь:", data)
    names  = [row[0] for row in data]
    phones = [row[1] for row in data]

    with connec.cursor() as cursor:
        cursor.execute(
            "CALL qwe(%s, %s)", (names,phones))
        bad = cursor.fetchone()[0]
        connec.commit()

        if bad:
            print("Неверные данные:", bad)
        else:
            print("Все данные верные!")


    # 4 limit and offset
    a=input()
    b=input()
    with connec.cursor() as cursor:
        cursor.execute(
            'select * from ddd(%s,%s)',(a,b)
        )
        e=cursor.fetchall()
        print(e)
        connec.commit()


    #5 Delete 
    name  = input("Имя (Enter если не знаешь): ")
    phone = input("Телефон (Enter если не знаешь): ")
    with connec.cursor() as cursor:
        cursor.execute('CALL rfd(%s, %s)', (name, phone))
        connec.commit()
        print("Удалено!")


    # Show all
    with connec.cursor() as cursor:
        cursor.execute(
            'select * from phonebook'
        )
        e=cursor.fetchall()
        print(e)
        for i in e:
            print(i)
        connec.commit()

except Exception as e:
    connec.rollback()
    print("Error:", e)

finally:
    if connec:
        connec.close()
        print("Connection closed")