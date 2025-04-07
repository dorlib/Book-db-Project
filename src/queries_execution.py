from queries_db_script import query_1, query_2, query_3, query_4, query_5, query_6

def main():
    print("Executing Query 1: 10 Most Recently Published Books")
    query_1()
    print("\nExecuting Query 2: List Books for the Subject 'fiction'")
    query_2()
    print("\nExecuting Query 3: List Books Published in 2000")
    query_3()
    print("\nExecuting Query 4: For Each Author, Find the Subject with the Most Books")
    query_4()
    print("\nExecuting Query 5: For Each Subject, Find the Decade with the Most Publications")
    query_5()
    print("\nExecuting Query 6: Percentage of Books per Subject Relative to Total Books")
    query_6()

if __name__ == "__main__":
    main()
