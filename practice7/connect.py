import psycopg2
from config import host, user, password,database,port

def ers():
    conn=psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port
    )
    return conn
