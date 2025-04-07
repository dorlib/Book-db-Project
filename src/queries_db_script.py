from utils import create_database_connection

# ---------------------------
# Simple SELECT Queries
# ---------------------------

def query_1():
    """
    Query 1: 10 Most Recently Published Books
    -----------------------------------------
    Retrieves the 10 newest books (by first_publish_year) along with one author.
    
    Example Output:
      | title                            | first_publish_year | author_name      |
      |----------------------------------|--------------------|------------------|
      | The Testaments                   | 2019               | Margaret Atwood  |
      | Normal People                    | 2018               | Sally Rooney     |
      | ...                              | ...                | ...              |
    """
    connection = create_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT 
            b.title, 
            b.first_publish_year, 
            a.name AS author_name
        FROM books b
        JOIN book_authors ba ON b.book_id = ba.book_id
        JOIN authors a ON ba.author_id = a.author_id
        WHERE b.first_publish_year IS NOT NULL
        ORDER BY b.first_publish_year DESC
        LIMIT 10;
    """)
    for row in cursor.fetchall():
        print(row)
    cursor.close()
    connection.close()

def query_2():
    """
    Query 2: Top 10 Oldest Books for a Specific Subject
    -----------------------------------------------------
    Retrieves the top 10 oldest books (based on first_publish_year) associated with the subject 'fiction'.
    This query uses a join between books, book_subjects, and subjects, and orders the result by first_publish_year.
    
    Example Output:
      | title                     | subject_name | first_publish_year |
      |---------------------------|--------------|--------------------|
      | The Old Man and the Sea   | fiction      | 1952               |
      | 1984                      | fiction      | 1949               |
      | ...                       | ...          | ...                |
    """
    connection = create_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT b.title, s.name AS subject_name, b.first_publish_year
        FROM books b
        JOIN book_subjects bs ON b.book_id = bs.book_id
        JOIN subjects s ON bs.subject_id = s.subject_id
        WHERE s.name = 'fiction'
          AND b.first_publish_year IS NOT NULL
        ORDER BY b.first_publish_year ASC
        LIMIT 10;
    """)
    for row in cursor.fetchall():
        print(row)
    cursor.close()
    connection.close()

def query_3():
    """
    Query 3: List Books Published in a Given Year (2000)
    -----------------------------------------------------
    Retrieves titles and first_publish_year for books published in 2000.
    
    Example Output:
      | title                | first_publish_year |
      |----------------------|--------------------|
      | Book Title Example   | 2000               |
    """
    connection = create_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT title, first_publish_year
        FROM books
        WHERE first_publish_year = 2000;
    """)
    for row in cursor.fetchall():
        print(row)
    cursor.close()
    connection.close()

# ---------------------------
# Complex Queries (Aggregation, Nesting, etc.)
# ---------------------------

def query_4():
    """
    Query 4: For Each Author, Find the Subject with the Most Books (Limited Output)
    -----------------------------------------------------------------------------------
    For every author (with at least 5 books), this query determines the subject in which they have
    the highest number of books. The output is limited to the top 20 rows sorted by book count.
    
    Example Output:
      | author_name      | subject_name | book_count |
      |------------------|--------------|------------|
      | J.K. Rowling     | fantasy      | 30         |
      | Stephen King     | horror       | 25         |
    """
    connection = create_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT a.name AS author_name,
               s.name AS subject_name,
               COUNT(*) AS book_count
        FROM authors a
        JOIN book_authors ba ON a.author_id = ba.author_id
        JOIN book_subjects bs ON ba.book_id = bs.book_id
        JOIN subjects s ON bs.subject_id = s.subject_id
        WHERE a.author_id IN (
            SELECT author_id
            FROM book_authors
            GROUP BY author_id
            HAVING COUNT(*) >= 5
        )
        GROUP BY a.author_id, s.subject_id
        HAVING COUNT(*) = (
            SELECT MAX(cnt)
            FROM (
                 SELECT COUNT(*) AS cnt
                 FROM book_authors ba2
                 JOIN book_subjects bs2 ON ba2.book_id = bs2.book_id
                 WHERE ba2.author_id = a.author_id
                 GROUP BY bs2.subject_id
            ) AS sub
        )
        ORDER BY book_count DESC
        LIMIT 20;
    """)
    for row in cursor.fetchall():
        print(row)
    cursor.close()
    connection.close()

def query_5():
    """
    Query 5: For Each Subject, Find the Decade with the Most Publications
    -------------------------------------------------------------------------
    For every subject, groups books by decade (based on first_publish_year) and returns the decade with the highest count.
    
    Example Output:
      | subject_name | decade | publication_count |
      |--------------|--------|-------------------|
      | fiction      | 1960   | 120               |
      | history      | 1950   | 80                |
    """
    connection = create_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT s.name AS subject_name, sub.decade, sub.pub_count AS publication_count
        FROM subjects s
        JOIN (
            SELECT bs.subject_id,
                   FLOOR(b.first_publish_year/10)*10 AS decade,
                   COUNT(*) AS pub_count
            FROM book_subjects bs
            JOIN books b ON bs.book_id = b.book_id
            WHERE b.first_publish_year IS NOT NULL
            GROUP BY bs.subject_id, decade
        ) AS sub ON s.subject_id = sub.subject_id
        WHERE sub.pub_count = (
            SELECT MAX(pub_count)
            FROM (
                 SELECT bs2.subject_id,
                        FLOOR(b2.first_publish_year/10)*10 AS decade,
                        COUNT(*) AS pub_count
                 FROM book_subjects bs2
                 JOIN books b2 ON bs2.book_id = b2.book_id
                 WHERE b2.first_publish_year IS NOT NULL
                 GROUP BY bs2.subject_id, decade
            ) AS sub2
            WHERE sub2.subject_id = s.subject_id
        )
        ORDER BY s.name;
    """)
    for row in cursor.fetchall():
        print(row)
    cursor.close()
    connection.close()

def query_6():
    """
    Query 6: For Each Subject, Find the Top Author and Their Average Publish Year
    ---------------------------------------------------------------------------------
    For every subject, this query finds the author with the most books in that subject (using a window function)
    and calculates the average first_publish_year for that author's books in that subject.
    
    Example Output:
      | subject_name | top_author       | book_count | avg_publish_year |
      |--------------|------------------|------------|------------------|
      | fiction      | Agatha Christie  | 66         | 1943.47          |
      | mystery      | Agatha Christie  | 83         | 1946.59          |
      | fantasy      | Terry Pratchett  | 40         | 1996.85          |
    """
    connection = create_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        WITH RankedAuthors AS (
            SELECT 
                s.subject_id,
                s.name AS subject_name,
                a.name AS top_author,
                COUNT(*) AS book_count,
                ROUND(AVG(b.first_publish_year), 2) AS avg_publish_year,
                ROW_NUMBER() OVER (PARTITION BY s.subject_id 
                                   ORDER BY COUNT(*) DESC, AVG(b.first_publish_year) DESC) AS rn
            FROM subjects s
            JOIN book_subjects bs ON s.subject_id = bs.subject_id
            JOIN books b ON bs.book_id = b.book_id
            JOIN book_authors ba ON b.book_id = ba.book_id
            JOIN authors a ON ba.author_id = a.author_id
            GROUP BY s.subject_id, a.author_id
        )
        SELECT subject_name, top_author, book_count, avg_publish_year
        FROM RankedAuthors
        WHERE rn = 1
        ORDER BY subject_name;
    """)
    results = cursor.fetchall()
    for row in results:
        subject_name, top_author, book_count, avg_publish_year = row
        print((subject_name, top_author, book_count, float(avg_publish_year)))
    cursor.close()
    connection.close()

if __name__ == "__main__":
    print("Executing Query 1:")
    query_1()
    print("\nExecuting Query 2:")
    query_2()
    print("\nExecuting Query 3:")
    query_3()
    print("\nExecuting Query 4:")
    query_4()
    print("\nExecuting Query 5:")
    query_5()
    print("\nExecuting Query 6:")
    query_6()
