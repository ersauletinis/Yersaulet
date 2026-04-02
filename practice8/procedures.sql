--2
create or replace procedure era(ph_ne varchar(50),phone varchar(20))
language plpgsql
as $$
declare 
	nwww varchar(50);
begin
	select name
	into nwww
	from phonebook
	where name=ph_ne;
	if not found then
		insert into phonebook(name,phone_number)
		values(ph_ne,phone);
	else
		update phonebook set phone_number=phone where name=ph_ne;
	end if;

end;
$$;
call era('Yersaulet','+7777777');


--3
create or replace procedure qwe(names TEXT[], phones TEXT[],INOUT result TEXT DEFAULT '')
returns table(bad_name TEXT, bad_phone TEXT)
language plpgsql
as $$ 
declare 
	i int;
	ph_name varchar(50);
	ph_phone varchar(20);
	bad_result text='';
begin
	for i in 1..array_length(names,1) loop
		ph_name:=names[i];
		ph_phone := phones[i];

		if ph_phone ~ '^\+[0-9]+$' THEN
			insert into phonebook(name,phone_number) 
			values(ph_name,ph_phone);
		else
			bad_result:=bad_result ||ph_name||'; '||ph_phone||', ';
		end if;
	end loop;
end;
$$;
call qwe(
    array['ers','daulet'],
    array['+7767747375','+7705868483']
);


--5
create or replace procedure rfd(ph_name varchar(50), ph_phone varchar(20))
language plpgsql
as $$
begin
	
	delete  from phonebook where name=ph_name or phone_number=ph_phone;

	if not found then
		raise exception  'Ничего не найдено';
	end if;
end;
$$;