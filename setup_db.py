"""Database setup script for the ATC application.

This script will connect to the MySQL server using the same credentials
used by `app.py` and it will ensure that the `airlines` database and
the necessary tables (`users` and `flights`) exist.  It also inserts a
default administrator account if one does not already exist.

Usage:
    python setup_db.py

Update the connection parameters below if your MySQL server uses
different credentials.
"""

import pymysql

# credentials - keep in sync with app.get_db_connection()
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "masterarun1",
}

DEFAULT_ADMIN = {
    "username": "admin",
    # WARNING: for a real application, do not hard-code passwords or store
    # them in plain text.  This example uses plain text for simplicity.
    "password": "adminpass",
    "role": "admin",
}


def create_database_and_tables():
    # create the database if it doesn't exist and build tables
    conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
    try:
        with conn.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS airlines")
            cursor.execute("USE airlines")

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    role VARCHAR(20) NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS flights (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    flight_id VARCHAR(20) UNIQUE NOT NULL,
                    flight_name VARCHAR(100) NOT NULL,
                    departure VARCHAR(10) NOT NULL,
                    arrival VARCHAR(10) NOT NULL,
                    route VARCHAR(100) NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """
            )
            conn.commit()

            # insert default admin if not present
            cursor.execute(
                "SELECT * FROM users WHERE username=%s", (DEFAULT_ADMIN["username"],)
            )
            if cursor.fetchone() is None:
                cursor.execute(
                    "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                    (DEFAULT_ADMIN["username"], DEFAULT_ADMIN["password"], DEFAULT_ADMIN["role"]),
                )
                conn.commit()
                print("Default admin user created (username=admin, password=adminpass)")
            else:
                print("Admin user already exists, skipping creation.")

    finally:
        conn.close()


if __name__ == "__main__":
    create_database_and_tables()
    print("Database setup complete.")
