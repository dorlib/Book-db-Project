# Book Database Management System

<p align="center">
    <img alt="Issues" src="https://img.shields.io/github/issues-raw/dorlib/Book-db-Project"/>
    <img alt="Pull Requests" src="https://img.shields.io/github/issues-pr-closed/dorlib/Book-db-Project"/>
    <img alt="Stars" src="https://img.shields.io/github/stars/dorlib/Book-db-Project?style=social">
    <img alt="Last Commit" src="https://img.shields.io/github/last-commit/dorlib/Book-db-Project">
    <img alt="Repo Size" src="https://img.shields.io/github/repo-size/dorlib/Book-db-Project">
</p>

## Overview

This project involves the creation of a book-centered database management system (DBMS) using MySQL and Python. The system retrieves book data from the Open Library API and stores it in a well-structured MySQL database. In addition, the project implements six distinct SQL queries to analyze the stored data—focusing on publication years, subject distributions, and author contributions. Although the main focus is on backend data management and query processing, the documentation also includes a frontend design outline for the intended application interface.

## Features

1. **Database Schema**:  
   The database consists of five tables:
   - **books** – Contains book details such as `book_id`, `title`, and `first_publish_year`.
   - **authors** – Contains author details such as `author_id` and `name`.
   - **subjects** – Contains subject information (with `subject_id` and `name`).
   - **book_authors** – Resolves the many-to-many relationship between books and authors.
   - **book_subjects** – Resolves the many-to-many relationship between books and subjects.

2. **Data Population**:  
   - The system uses the Open Library API to retrieve book data across multiple subjects (e.g., fiction, fantasy, science, history, mystery, romance, biography, philosophy).
   - The insertion process is designed to accumulate at least 10,000 rows in total across all tables.

3. **Queries**:  
   - **Simple Queries:**  
     - **Query 1:** Retrieve the 10 most recently published books along with one associated author.
     - **Query 2:** Retrieve the top 10 oldest books for the subject “fiction.”
     - **Query 3:** Retrieve books published in the year 2000.
   - **Complex Queries:**  
     - **Query 4:** For each author (with at least 5 books), find the subject in which they have published the most books.
     - **Query 5:** For each subject, determine the decade with the highest number of publications.
     - **Query 6:** For each subject, find the top author (by book count) and calculate the average publication year for that author’s books.
   
4. **Database Optimizations**:  
   - Indexes are applied only on columns used by current queries to ensure efficient query execution:
     - **`idx_books_first_publish_year`** on `books(first_publish_year)` – Helps Queries 1, 3, 5, and 6.
     - **`idx_book_authors_author`** on `book_authors(author_id)` – Helps Queries 1, 4, and 6.
     - **`idx_book_subjects_subject`** on `book_subjects(subject_id)` – Helps Queries 2, 5, and 6.
     - **`idx_subjects_name`** on `subjects(name)` – Helps Query 2.

## Prerequisites

- Python 3.11.4
- MySQL server (hosted on `mysqlsrv1.cs.tau.ac.il`)
- Required Python libraries (see `requirements.txt`)

## File Structure

```
project-root/
│
├── src/
│   ├── create_db_script.py       # Script to create the database schema
│   ├── api_data_retrieve.py      # Script to fetch and insert data from TMDB API
│   ├── queries_db_script.py      # Contains the SQL query functions
│   └── queries_execution.py      # Demonstrates query executions
│
├── documentation/
│   ├── answers.pdf           # theoretical questions
│   └── mysql_and_user_password.txt # MySQL credentials
│
├── requirements.txt              # Required Python packages
└── name_and_id.txt               # Team member names and IDs
```


## Database Design

The database schema is as follows:

1. **books**  
   - **Columns:** `book_id` (PK), `title`, `first_publish_year`  
   - **Description:** Stores essential information about each book.

2. **authors**  
   - **Columns:** `author_id` (PK), `name`  
   - **Description:** Contains details of each author.

3. **subjects**  
   - **Columns:** `subject_id` (PK, auto-increment), `name` (unique)  
   - **Description:** Categorizes books by subject.

4. **book_authors**  
   - **Columns:** `book_id` (FK), `author_id` (FK)  
   - **Description:** Resolves the many-to-many relationship between books and authors.

5. **book_subjects**  
   - **Columns:** `book_id` (FK), `subject_id` (FK)  
   - **Description:** Resolves the many-to-many relationship between books and subjects.

## Queries Implemented

1. **Query 1: 10 Most Recently Published Books**  
   Retrieves the 10 newest books (by publication year) along with one associated author.

2. **Query 2: Top 10 Oldest Books for “fiction”**  
   Retrieves the 10 oldest books (by publication year) that belong to the subject “fiction.”

3. **Query 3: Books Published in 2000**  
   Retrieves books published in the year 2000.

4. **Query 4: For Each Author, Find the Subject with the Most Books**  
   Determines, for authors with at least 5 books, the subject in which they have the highest number of books (using aggregation and nested subqueries).

5. **Query 5: For Each Subject, Find the Decade with the Most Publications**  
   Groups books by decade per subject and returns the decade with the highest count.

6. **Query 6: For Each Subject, Find the Top Author and Their Average Publish Year**  
   Uses window functions to determine, for each subject, the top author (by book count) and calculates the average publication year for that author’s books.

## Index Strategy

The following indexes are applied to optimize the current queries:

| Table              | Index Name                        | Columns                         | Query Benefit                                                                    |
| ------------------ | --------------------------------- | ------------------------------- | -------------------------------------------------------------------------------- |
| **books**          | `idx_books_first_publish_year`    | `first_publish_year`            | Speeds up filtering and ordering in Queries 1, 3, 5, and 6 (e.g., sorting books by year). |
| **book_authors**   | `idx_book_authors_author`         | `author_id`                     | Optimizes joins and groupings by author in Queries 1, 4, and 6.                   |
| **book_subjects**  | `idx_book_subjects_subject`       | `subject_id`                    | Improves joins on subject in Queries 2, 5, and 6.                                |
| **subjects**       | `idx_subjects_name`               | `name`                          | Accelerates filtering for a specific subject (e.g., 'fiction') in Query 2.         |

## Setup and Usage

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create the Database

Run the following script to create the database schema:

```bash
python src/create_db_script.py
```

### 3. Populate the Database

Fetch and insert data from TMDB API:

```bash
python src/api_data_retrieve.py
```

### 4. Execute Queries

Run example queries to interact with the database:

```bash
python src/queries_execution.py
```

## System Documentation

Detailed descriptions of the database schema, design rationale, and optimizations are available in `system_docs.pdf`.

## Error Handling

The scripts include robust error handling to manage API failures, database connection issues, and data insertion conflicts.

## License

This project is developed for educational purposes and follows the academic guidelines set by the institution.

---

## Creators / Maintainers

- Shai Goldbourt([Shaigoldbourt22](https://github.com/Shaigoldbourt22))
- Dor Liberman ([dorlib](https://github.com/dorlib))

If you have any questions or feedback, I would be glad if you will contact us via mail.

<p align="left">
  <a href="dorlibrm@gmail.com"> 
    <img alt="Connect via Email" src="https://img.shields.io/badge/Gmail-c14438?style=flat&logo=Gmail&logoColor=white" />
  </a>
</p>

This project was created for educational purposes, for personal and open-source use.

If you like my content or find my code useful, give it a :star:

---
