import os
import logging
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

load_dotenv()

def get_postgres_connection():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

def execute_db_operation(operation, params=None, fetch=False, max_retries=3):
    conn = get_postgres_connection()
    try:
        with conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                for attempt in range(max_retries):
                    try:
                        if callable(operation):
                            result = operation(cur)
                        else:
                            cur.execute(operation, params or ())
                            if fetch:
                                result = cur.fetchall()
                        conn.commit()
                        if fetch:
                            return result
                        return
                    except psycopg2.Error as e:
                        conn.rollback()
                        logging.error(f"Database error (attempt {attempt + 1}/{max_retries}): {e}")
                        if attempt == max_retries - 1:
                            raise e
    finally:
        conn.close()

def execute_query(query, params=None):
    execute_db_operation(query, params)

def fetch_query(query, params=None):
    return execute_db_operation(query, params, fetch=True)

def initialize_database():
    operations = [
        '''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS salary (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            amount REAL NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            UNIQUE(user_id, month, year)
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            name TEXT NOT NULL,
            UNIQUE(user_id, name)
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS expenses (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            category_id INTEGER REFERENCES categories(id),
            amount REAL NOT NULL,
            description TEXT,
            date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    ]
    for operation in operations:
        execute_db_operation(operation)
    
    default_categories = ['Eat & Drink', 'Rent', 'Transportation', 'Utilities', 'Entertainment', 'Shopping', 'Healthcare', 'Education']
    existing_categories = execute_db_operation("SELECT name FROM categories WHERE user_id IS NULL", fetch=True)
    existing_category_names = [cat['name'] for cat in existing_categories] if existing_categories else []
    for category in default_categories:
        if category not in existing_category_names:
            execute_db_operation(
                "INSERT INTO categories (name, user_id) VALUES (%s, NULL)",
                (category,)
            )

def check_tables_exist():
    tables = ['users', 'salary', 'categories', 'expenses']
    for table in tables:
        result = execute_db_operation(f"SELECT to_regclass('public.{table}')", fetch=True)
        if result and result[0][0]:
            logging.info(f"Table '{table}' exists.")
        else:
            logging.warning(f"Table '{table}' does not exist.")

# Remove migrate_database and migrate_salary_table functions as they are no longer needed for PostgreSQL
