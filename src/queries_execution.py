from queries_db_script import query_1, query_2, query_3, query_4, query_5, query_6

def main():
    print("Executing Query 1: List Restaurants with Their Categories")
    query_1()
    print("\nExecuting Query 2: List Users and the Restaurants They Have Reviewed")
    query_2()
    print("\nExecuting Query 3: Show Reviews for 'Joe''s Pizza'")
    query_3()
    print("\nExecuting Query 4: Top 5 Restaurants by Average Rating (with at least 5 reviews)")
    query_4()
    print("\nExecuting Query 5: Most Common Category Among Highly Rated Restaurants")
    query_5()
    print("\nExecuting Query 6: For Each Category, Find the Restaurant with the Highest Number of Reviews")
    query_6()

if __name__ == "__main__":
    main()
