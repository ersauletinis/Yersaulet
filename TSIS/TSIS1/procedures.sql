-- 1. Добавить телефон контакту
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR, 
    p_phone VARCHAR,
    p_type VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_id INTEGER;
BEGIN
    SELECT id INTO v_id FROM phonebook WHERE name = p_contact_name;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Контакт не найден';
    END IF;
    INSERT INTO phones(phonebook_id, phone, type) VALUES (v_id, p_phone, p_type);
END;
$$;


-- 2. Переместить контакт в группу
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_group_id INTEGER;
BEGIN
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
    IF NOT FOUND THEN
        INSERT INTO groups(name) VALUES (p_group_name) RETURNING id INTO v_group_id;
    END IF;
    UPDATE phonebook SET group_id = v_group_id WHERE name = p_contact_name;
END;
$$;


-- 3. Поиск по имени, email и телефонам
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(name VARCHAR, email VARCHAR, birthday DATE, group_name VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT c.name, c.email, c.birthday, g.name
    FROM phonebook c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE c.name  ILIKE '%' || p_query || '%'
       OR c.email ILIKE '%' || p_query || '%'
       OR p.phone ILIKE '%' || p_query || '%';
END;
$$;

create or replace function ddd(ph_nm int ,ph_size int)
returns table(name varchar(50), phone_number varchar(20))
language plpgsql
as $$
begin
	return query
		select e.name ,e.phone_number
		from phonebook e
		limit ph_size
		offset (ph_nm-1)*ph_size;
end;
$$;