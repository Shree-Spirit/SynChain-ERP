import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="synchain_erp",
    user="postgres",
    password="shrig12345"
)
print("Connected successfully!")
conn.close()