from dotenv import load_dotenv
from utils import create_database_connection
import os
import requests
import time

load_dotenv()

# Base URL for Open Library search endpoint
BASE_URL = "https://openlibrary.org/search.json"

# List of subjects to query (you can add more subjects to increase variety)
subjects_list = ["fiction", "fantasy", "science", "history", "mystery", "romance", "biography", "philosophy"]

# SQL insert statements
insert_book = """INSERT INTO books (book_id, title, first_publish_year)
                 VALUES (%s, %s, %s)
                 ON DUPLICATE KEY UPDATE title = title"""
insert_author = """INSERT INTO authors (author_id, name)
                   VALUES (%s, %s)
                   ON DUPLICATE KEY UPDATE name = name"""
# For subjects, we insert only the name (subject_id is auto-increment)
insert_subject = """INSERT INTO subjects (name)
                    VALUES (%s)
                    ON DUPLICATE KEY UPDATE name = name"""
insert_book_author = """INSERT IGNORE INTO book_authors (book_id, author_id)
                        VALUES (%s, %s)"""
insert_book_subject = """INSERT IGNORE INTO book_subjects (book_id, subject_id)
                         VALUES (%s, %s)"""

def clean_database():
    connection = create_database_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM book_subjects")
    cursor.execute("DELETE FROM book_authors")
    cursor.execute("DELETE FROM subjects")
    cursor.execute("DELETE FROM authors")
    cursor.execute("DELETE FROM books")
    connection.commit()
    cursor.close()
    connection.close()

def insert_data():
    connection = create_database_connection()
    cursor = connection.cursor()

    books_batch = []
    authors_batch = []
    book_authors_batch = []
    subjects_batch = []   # Will be used later to insert unique subjects
    book_subjects_batch = []  # Temporary batch of (book_id, subject_name)

    # Use a set to accumulate unique subjects from all docs.
    subjects_set = set()

    max_pages = 10  # Number of pages per subject (each page returns up to 100 results)
    total_docs = 0

    for subject in subjects_list:
        print(f"Processing subject: {subject}")
        for page in range(1, max_pages + 1):
            params = {
                "subject": subject,
                "limit": 100,
                "page": page
            }
            response = requests.get(BASE_URL, params=params)
            data = response.json()
            docs = data.get("docs", [])
            if not docs:
                break

            for doc in docs:
                # Use the "key" field as the book_id (e.g., "/works/OL12345W")
                book_id = doc.get("key")
                title = doc.get("title")
                first_publish_year = doc.get("first_publish_year")
                if not book_id or not title:
                    continue
                books_batch.append((book_id, title, first_publish_year))
                total_docs += 1

                # Process authors (there may be multiple)
                author_keys = doc.get("author_key", [])
                author_names = doc.get("author_name", [])
                if author_keys and author_names and len(author_keys) == len(author_names):
                    for a_id, a_name in zip(author_keys, author_names):
                        authors_batch.append((a_id, a_name))
                        book_authors_batch.append((book_id, a_id))

                # Process subjects: if the doc does not include any subjects, use the queried subject as fallback.
                doc_subjects = doc.get("subject", [])
                if not doc_subjects:
                    print(f"Book {book_id} has no subjects; assigning fallback subject: {subject}")
                    doc_subjects = [subject]
                for subj in doc_subjects:
                    subjects_set.add(subj)
                    # Save (book_id, subject name) for later processing.
                    book_subjects_batch.append((book_id, subj))
            
            # Insert batches for the current page
            if books_batch:
                cursor.executemany(insert_book, books_batch)
                books_batch = []
            if authors_batch:
                cursor.executemany(insert_author, authors_batch)
                authors_batch = []
            if book_authors_batch:
                cursor.executemany(insert_book_author, book_authors_batch)
                book_authors_batch = []
            
            connection.commit()
            print(f"Processed page {page} for subject '{subject}', total docs so far: {total_docs}")
            time.sleep(1)  # be polite to the API

    # Insert unique subjects collected in subjects_set
    for subj in subjects_set:
        subjects_batch.append((subj,))
    if subjects_batch:
        cursor.executemany(insert_subject, subjects_batch)
        connection.commit()
        print(f"Inserted {len(subjects_batch)} unique subjects.")

    # Now, rebuild the book_subjects batch to use subject_id instead of subject name.
    subject_mapping = {}
    cursor.execute("SELECT subject_id, name FROM subjects")
    for subj_id, subj_name in cursor.fetchall():
        subject_mapping[subj_name] = subj_id

    book_subjects_with_ids = []
    for b_id, subj_name in book_subjects_batch:
        subj_id = subject_mapping.get(subj_name)
        if subj_id:
            book_subjects_with_ids.append((b_id, subj_id))
    
    if book_subjects_with_ids:
        cursor.executemany(insert_book_subject, book_subjects_with_ids)
    
    connection.commit()
    cursor.close()
    connection.close()
    print("Data insertion complete.")

if __name__ == "__main__":
    clean_database()
    insert_data()
