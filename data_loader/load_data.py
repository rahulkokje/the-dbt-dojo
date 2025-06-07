import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

conn = psycopg2.connect(
    dbname="dojo_db",
    user="the_dbt_dojo_user",
    password="the_dbt_dojo_pass",
    host="postgres",
    port=5432
)
cur = conn.cursor()


def load_csv_to_table(csv_path, table_name, schema="raw"):
    df = pd.read_csv(csv_path)

    # Create schema if not exists
    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema};")

    # Dynamically create the table if it doesn't exist
    columns = ", ".join([f"{col} TEXT" for col in df.columns])
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {schema}.{table_name} (
            {columns}
        );
        TRUNCATE TABLE {schema}.{table_name};
    """)

    # Insert data
    tuples = [tuple(x) for x in df.values]
    cols = ", ".join(df.columns)
    insert_sql = f"INSERT INTO {schema}.{table_name} ({cols}) VALUES %s"
    execute_values(cur, insert_sql, tuples)
    conn.commit()
    print(f"Loaded {len(df)} rows into {schema}.{table_name}")


# Load all CSVs
load_csv_to_table("data/customers.csv", "customers")
load_csv_to_table("data/accounts.csv", "accounts")
load_csv_to_table("data/transactions.csv", "transactions")

cur.close()
conn.close()
