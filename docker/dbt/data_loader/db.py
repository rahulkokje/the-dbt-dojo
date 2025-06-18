import psycopg2


def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="dojo_db",
        user="dojo_user",
        password="dojo_pass"
    )
