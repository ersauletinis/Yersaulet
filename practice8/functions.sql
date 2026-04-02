--1
create or replace function sa(pattern text)
returns TABLE(id int,name varchar(50),phone_number varchar(20)) 
language plpgsql 
as $$
begin 
	return query
		select e.id,e.name, e.phone_number 
		from phonebook e
        WHERE e.name    ILIKE '%' || pattern || '%'
           OR e.phone_number  ILIKE '%' || pattern || '%';
end;
$$;


--4
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