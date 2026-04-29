import json
import csv
from connect import ers

connec = ers()

try:
    # 3.2.1 — Фильтр по группе
    def filter_by_group():
        group = input("Группа (Family/Work/Friend/Other): ")
        with connec.cursor() as cursor:
            cursor.execute("""
                SELECT c.name, c.email, g.name
                FROM phonebook c
                JOIN groups g ON g.id = c.group_id
                WHERE g.name ILIKE %s
            """, (group,))
            for row in cursor.fetchall():
                print(row)

    # 3.2.2 — Поиск по email
    def search_by_email():
        email = input("Email (например gmail): ")
        with connec.cursor() as cursor:
            cursor.execute("""
                SELECT name, email FROM phonebook
                WHERE email ILIKE %s
            """, (f'%{email}%',))
            for row in cursor.fetchall():
                print(row)

    # 3.2.3 — Сортировка
    def sorted_contacts():
        print("Сортировка: 1-имя  2-день рождения  3-дата добавления")
        choice = input("Выбор: ")
        order = {"1": "name", "2": "birthday", "3": "id"}.get(choice, "name")
        with connec.cursor() as cursor:
            cursor.execute(f"SELECT name, email, birthday FROM phonebook ORDER BY {order}")
            for row in cursor.fetchall():
                print(row)

    # 3.2.4 — Пагинация
    def paginated():
        page = 1
        size = 2
        while True:
            with connec.cursor() as cursor:
                cursor.execute("SELECT * FROM ddd(%s, %s)", (page, size))
                rows = cursor.fetchall()
                if not rows:
                    print("Больше нет контактов")
                    break
                for row in rows:
                    print(row)
            cmd = input("next / prev / quit: ")
            if cmd == "next":
                page += 1
            elif cmd == "prev" and page > 1:
                page -= 1
            elif cmd == "quit":
                break

    # 3.3.1 — Экспорт в JSON
    def export_json():
        with connec.cursor() as cursor:
            cursor.execute("""
                SELECT c.name, c.email, c.birthday::text,
                        g.name as group_name,
                        array_agg(p.phone) as phones
                FROM phonebook c
                LEFT JOIN groups g ON g.id = c.group_id
                LEFT JOIN phones p ON p.contact_id = c.id
                GROUP BY c.name, c.email, c.birthday, g.name
            """)
            rows = cursor.fetchall()
        data = [{"name": r[0], "email": r[1], "birthday": r[2],
                    "group": r[3], "phones": r[4]} for r in rows]
        with open("contacts.json", "w") as f:
            json.dump(data, f, indent=2)
        print("Сохранено в contacts.json")

    # 3.3.2 — Импорт из JSON
    def import_json():
        with open("TSIS1/contacts.json", "r") as f:
            data = json.load(f)
        with connec.cursor() as cursor:
            for c in data:
                cursor.execute("SELECT id FROM phonebook WHERE name=%s", (c["name"],))
                exists = cursor.fetchone()
                if exists:
                    choice = input(f"{c['name']} уже есть. skip/overwrite: ")
                    if choice == "skip":
                        continue
                    cursor.execute("""
                        UPDATE phonebook SET email=%s, birthday=%s WHERE name=%s
                    """, (c["email"], c["birthday"], c["name"]))
                else:
                    cursor.execute("""
                        INSERT INTO phonebook(name, email, birthday)
                        VALUES (%s, %s, %s)
                    """, (c["name"], c["email"], c["birthday"]))
            connec.commit()
        print("Импорт завершён")

    # 3.3.3 — Импорт из CSV
    def import_csv():
        with open(r"C:\Users\noutshopkz\OneDrive\Desktop\qazaq\TSIS\TSIS1\contacts.csv", "r") as f:
            reader = csv.reader(f)
            with connec.cursor() as cursor:
                for row in reader:
                    name, phone_number, email, birthday, group, phone_type = row
                    cursor.execute("SELECT id FROM groups WHERE name=%s", (group,))
                    group_row = cursor.fetchone()
                    group_id = group_row[0] if group_row else None
                    cursor.execute("""
                        INSERT INTO phonebook(name, email, birthday, group_id)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (name, email, birthday, group_id))
                    cursor.execute("""
                        INSERT INTO phones(contact_id, phone, type)
                        SELECT id, %s, %s FROM phonebook WHERE name=%s
                    """, (phone_number, phone_type, name))
                connec.commit()
        print("CSV импорт завершён")

    # 3.4.1 — Добавить телефон контакту
    def add_phone():
        name = input("Имя контакта: ")
        phone = input("Номер телефона: ")
        phone_type = input("Тип (home/work/mobile): ")
        with connec.cursor() as cursor:
            cursor.execute(
                "CALL add_phone(%s, %s, %s)", (name, phone, phone_type))
            connec.commit()
            print("Телефон добавлен!")

    # 3.4.2 — Переместить контакт в группу
    def move_to_group():
        name = input("Имя контакта: ")
        group = input("Группа (Family/Work/Friend/Other): ")
        with connec.cursor() as cursor:
            cursor.execute(
                "CALL move_to_group(%s, %s)", (name, group))
            connec.commit()
            print("Контакт перемещён в группу!")

    # 3.4.3 — Поиск по имени, email и телефону
    def search_contacts():
        query = input("Поиск: ")
        with connec.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM search_contacts(%s)", (query,))
            rows = cursor.fetchall()
            connec.commit()
            if rows:
                for row in rows:
                    print(row)
            else:
                print("Ничего не найдено")

    # Показать все контакты
    def show_all():
        with connec.cursor() as cursor:
            cursor.execute("SELECT * FROM phonebook")
            for row in cursor.fetchall():
                print(row)

    # Меню
    while True:
        print("\n=== МЕНЮ ===")
        print("1 — Фильтр по группе")
        print("2 — Поиск по email")
        print("3 — Сортировка")
        print("4 — Пагинация")
        print("5 — Экспорт в JSON")
        print("6 — Импорт из JSON")
        print("7 — Импорт из CSV")
        print("8 — Показать все контакты")
        print("9 — Добавить телефон контакту")
        print("10 — Переместить контакт в группу")
        print("11 — Поиск по имени/email/телефону")
        print("0 — Выход")

        choice = input("Выбор: ")

        if choice == "1":
            filter_by_group()
        elif choice == "2":
            search_by_email()
        elif choice == "3":
            sorted_contacts()
        elif choice == "4":
            paginated()
        elif choice == "5":
            export_json()
        elif choice == "6":
            import_json()
        elif choice == "7":
            import_csv()
        elif choice == "8":
            show_all()
        elif choice == "9":
            add_phone()
        elif choice == "10":
            move_to_group()
        elif choice == "11":
            search_contacts()
        elif choice == "0":
            print("Выход")
            break
        else:
            print("Неверный выбор, попробуй снова")

except Exception as e:
    connec.rollback()
    print("Ошибка:", e)

finally:
    if connec:
        connec.close()
        print("Соединение закрыто")
 