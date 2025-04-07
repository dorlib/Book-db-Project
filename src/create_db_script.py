from utils import create_database_connection
from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()

db_name = os.getenv('DB_NAME')
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

def create_database():
    connection = create_database_connection()
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    cursor.close()
    connection.close()

def create_tables():
    connection = create_database_connection()
    cursor = connection.cursor()

    # Create table: books
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        book_id VARCHAR(255) PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        first_publish_year INT
    )
    """)

    # Create table: authors
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS authors (
        author_id VARCHAR(255) PRIMARY KEY,
        name VARCHAR(255) NOT NULL
    )
    """)

    # Create table: subjects
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        subject_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL
    )
    """)

    # Create join table: book_authors
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS book_authors (
        book_id VARCHAR(255),
        author_id VARCHAR(255),
        PRIMARY KEY (book_id, author_id),
        FOREIGN KEY (book_id) REFERENCES books(book_id),
        FOREIGN KEY (author_id) REFERENCES authors(author_id)
    )
    """)

    # Create join table: book_subjects
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS book_subjects (
        book_id VARCHAR(255),
        subject_id INT,
        PRIMARY KEY (book_id, subject_id),
        FOREIGN KEY (book_id) REFERENCES books(book_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
    )
    """)

    # Create indexes relevant to our current queries:
    def create_index_if_not_exists(index_name, table_name, index_sql):
        cursor.execute(f"""
        SELECT COUNT(*)
        FROM information_schema.statistics
        WHERE table_schema = '{db_name}' 
          AND table_name = '{table_name}' 
          AND index_name = '{index_name}'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute(index_sql)

    # Index on books.first_publish_year for queries filtering and grouping on publication year.
    create_index_if_not_exists("idx_books_first_publish_year", "books",
        "CREATE INDEX idx_books_first_publish_year ON books(first_publish_year)")

    # Index on book_authors.author_id for faster joins/grouping on author.
    create_index_if_not_exists("idx_book_authors_author", "book_authors",
        "CREATE INDEX idx_book_authors_author ON book_authors(author_id)")

    # Index on book_subjects.subject_id for faster joins/grouping on subject.
    create_index_if_not_exists("idx_book_subjects_subject", "book_subjects",
        "CREATE INDEX idx_book_subjects_subject ON book_subjects(subject_id)")

    # Index on subjects.name to optimize filtering on subject name.
    create_index_if_not_exists("idx_subjects_name", "subjects",
        "CREATE INDEX idx_subjects_name ON subjects(name)")

    connection.commit()
    cursor.close()
    connection.close()

if __name__ == "__main__":
    create_database()
    create_tables()
