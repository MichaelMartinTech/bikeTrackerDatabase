"""
Author: Michael R. Martin
File Name: bikeWishList/main.py
Date Created: 12/11/2024
Description:
    This CLI system manages one or multiple bike wishlists using a PostgreSQL database. 
    Users can add, remove, and view wishlists and manage products within those wishlists.

This code uses:
    - psycopg - PostgreSQL database connection)
    - getpass - Password input
    - msvcrt - Key press handling
Use:
    - Ensure "bikewish" database is set up.
    - Run code and follow command-line prompts
"""
# Libraries
import psycopg  # Database access
import getpass  # Password access
from msvcrt import getch  # Key press progression


# Prompt for Password
def get_password():
    # Password attempts
    attempts = 3
    while attempts > 0:
        password = getpass.getpass("Enter your database password: ")
        if password:
            return password
        else:
            attempts -= 1
            print(f"Invalid input. You have {attempts} attempts remaining.")

    print("Maximum attempts exceeded. Press any key to exit program...")
    getch()  # Key press without requiring Enter
    exit()


# Database Connection
"""
Function name: get_connection
Input: password (String; Database password)
Output: psycopg.Connection object or None if connection fails.
Description: Establish and return a connection to the PostgreSQL 
    database.
"""


def get_connection(password):
    try:
        return psycopg.connect(
            f"dbname=bikewish user=postgres password={password} host=localhost port=5432"
        )
    except psycopg.OperationalError as e:
        print("Error: Unable to connect to the database.")
        print(f"Details: {e}")
        return None


## ListTracker Class
"""
Class Name: ListTracker
Attributes:
    - wishlist_name: Name of the wishlist.
Methods:
    - __init__: Initialize wishlist object with a given name.
    - get_all_wishlists: Fetch all wishlists from the database.
    - createList: Add a new wishlist to the database.
    - deleteList: Remove a wishlist from the database.
    - get_product_details: Display product details by category or all products.
    - viewList: Manage items in a specific wishlist.
Description: Manage wishlists and their items in the database.
"""
class ListTracker:
    # Initialize ListTracker object
    def __init__(self, wishlist_name):
        self.wishlist_name = wishlist_name

    @staticmethod
    def get_all_wishlists(conn):
        with conn.cursor() as cur:
            cur.execute('SELECT "wishlist_name" FROM "List_Tracker"')
            rows = cur.fetchall()
            return [ListTracker(row[0]) for row in rows]

    @staticmethod
    def createList(conn, wishlist_name):
        if wishlist_name.strip().lower() == "exit":
            print("Operation canceled.")
            return
        with conn.cursor() as cur:
            cur.execute(
                'SELECT "wishlist_name" FROM "List_Tracker" WHERE "wishlist_name" = %s',
                (wishlist_name,),
            )
            if cur.fetchone():
                print(f"Wishlist '{wishlist_name}' already exists.")
                return

            cur.execute(
                'INSERT INTO "List_Tracker" ("wishlist_name") VALUES (%s)',
                (wishlist_name,),
            )
            conn.commit()
            print(f"Wishlist '{wishlist_name}' added successfully.")

    @staticmethod
    def deleteList(conn, wishlist_name):
        if wishlist_name.strip().lower() == "exit":
            print("Operation canceled.")
            return
        with conn.cursor() as cur:
            cur.execute('SELECT "wishlist_name" FROM "List_Tracker"')
            rows = cur.fetchall()
            wishlists = [row[0] for row in rows]

            if wishlist_name not in wishlists:
                # Check for similar names
                similar = [
                    wl for wl in wishlists if wishlist_name.lower() in wl.lower()
                ]
                if similar:
                    print(
                        f"Wishlist '{wishlist_name}' does not exist. Did you mean: {', '.join(similar)}?"
                    )
                else:
                    print(f"Wishlist '{wishlist_name}' does not exist.")
                return

            cur.execute(
                'DELETE FROM "List_Tracker" WHERE "wishlist_name" = %s',
                (wishlist_name,),
            )
            conn.commit()
            print(f"Wishlist '{wishlist_name}' removed successfully.")

    """
    Function name: get_product_details
    Input: conn (Database connection object)
    Output: None
    Description: Provides a menu for the user to view and 
    filter products by category. Uses SQL queries to fetch 
    product details from the database.
    """

    @staticmethod
    def get_product_details(conn):
        # Displays the product search menu, allowing users to filter by category or view all products.
        def fetch_products_by_category(category_id=None):
            with conn.cursor() as cur:
                if category_id:
                    cur.execute(
                        "SELECT p.product_id, p.product_name, c.category_name "
                        'FROM "Products" p '
                        'JOIN "Categories" c ON p.category_id = c.category_id '
                        "WHERE p.category_id = %s",
                        (category_id,),
                    )
                else:
                    cur.execute(
                        "SELECT p.product_id, p.product_name, c.category_name "
                        'FROM "Products" p '
                        'JOIN "Categories" c ON p.category_id = c.category_id'
                    )
                return cur.fetchall()

        def list_categories():
            with conn.cursor() as cur:
                cur.execute('SELECT category_id, category_name FROM "Categories"')
                return cur.fetchall()

        categories = list_categories()
        current_category = None

        while True:
            products = fetch_products_by_category(current_category)
            category_name = (
                "All"
                if current_category is None
                else next(
                    (cat[1] for cat in categories if cat[0] == current_category),
                    "Unknown",
                )
            )

            print(f"\nAvailable Products (Category: {category_name}):")
            if not products:
                print("No products found.")
            else:
                for product in products:
                    print(f"ID: {product[0]}, Name: {product[1]}, Type: {product[2]}")

            print("\nOptions:")
            print("1. Change Category")
            print("2. Return to Wishlist Menu")

            choice = input("Enter your choice: ").strip()
            if choice == "1":
                print("\nAvailable Categories:")
                for category in categories:
                    print(f"ID: {category[0]}, Name: {category[1]}")
                print("Enter 'all' to view all products.")
                category_input = input("Enter category ID: ").strip().lower()
                if category_input == "all":
                    current_category = None
                else:
                    try:
                        current_category = int(category_input)
                        if not any(cat[0] == current_category for cat in categories):
                            print("Invalid category. Showing all products.")
                            current_category = None
                    except ValueError:
                        print("Invalid input. Showing all products.")
                        current_category = None
            elif choice == "2":
                break
            else:
                print("Invalid choice. Please try again.")

    """
    Function name: viewList
    Input:
    - conn (Database connection object)
    - wishlist_name (String, the name of the wishlist to view)
    Output: None
    Description: Displays the contents of a specific wishlist. 
        Allows the user to perform operations like adding/removing 
        items, modifying quantities, and updating ownership status.
    """

    @staticmethod
    def viewList(conn, wishlist_name):
        if wishlist_name.strip().lower() == "exit":
            print("Operation canceled.")
            return
        with conn.cursor() as cur:
            cur.execute('SELECT "wishlist_name" FROM "List_Tracker"')
            rows = cur.fetchall()
            wishlists = [row[0] for row in rows]

            if wishlist_name not in wishlists:
                print(f"Wishlist '{wishlist_name}' does not exist.")
                return

            while True:

                def fetch_items():
                    with conn.cursor() as cur:
                        cur.execute(
                            'SELECT p.product_id, p.product_name, wl.number, wl.owned FROM "Wish_List" wl JOIN "Products" p ON wl.product_id = p.product_id WHERE wl.wishlist_name = %s',
                            (wishlist_name,),
                        )
                        return cur.fetchall()

                # Refresh 'items' after each loop
                items = fetch_items()

                # List items
                if not items:
                    print(f"The wishlist '{wishlist_name}' is empty.")
                else:
                    print(f"\nItems in Wishlist '{wishlist_name}':")
                    for item in items:
                        status = "Owned" if item[3] else "Not Owned"
                        print(
                            f"ID: {item[0]}, Name: {item[1]}, Quantity: {item[2]}, Status: {status}"
                        )

                # Options
                print("\nOptions:")
                print("1. View Products")
                print("2. Add Item by ID")
                print("3. Add Item by Name")
                print("4. Remove Item")
                print("5. Modify Quantity")
                print("6. Modify Ownership Status")
                print("7. Back to Main Menu")

                choice = input("Enter your choice: ")
                if choice == "1":
                    ListTracker.get_product_details(conn)
                elif choice == "2":
                    product_id = input(
                        "Enter the product ID to add (or type 'exit' to cancel): "
                    ).strip()
                    if product_id.lower() == "exit":
                        print("Operation canceled.")
                        continue

                    # Check if the product already exists in the wishlist
                    with conn.cursor() as cur:
                        cur.execute(
                            'SELECT product_id FROM "Wish_List" WHERE wishlist_name = %s AND product_id = %s',
                            (wishlist_name, product_id),
                        )
                        if cur.fetchone():
                            print("You already have this product in your wishlist.")
                            continue

                    quantity = input(
                        "Enter the quantity (or type 'exit' to cancel): "
                    ).strip()
                    if quantity.lower() == "exit":
                        print("Operation canceled.")
                        continue
                    try:
                        quantity = int(quantity)
                    except ValueError:
                        print("Invalid quantity. Please enter a number.")
                        continue

                    with conn.cursor() as cur:
                        cur.execute(
                            'INSERT INTO "Wish_List" (wishlist_name, product_id, number, owned) VALUES (%s, %s, %s, FALSE)',
                            (wishlist_name, product_id, quantity),
                        )
                        conn.commit()
                    print("Item added successfully.")
                elif choice == "3":
                    product_name = input(
                        "Enter the product name to add (or type 'exit' to cancel): "
                    ).strip()
                    if product_name.lower() == "exit":
                        print("Operation canceled.")
                        continue

                    with conn.cursor() as cur:
                        cur.execute(
                            'SELECT product_id, product_name FROM "Products" WHERE product_name ILIKE %s',
                            (f"%{product_name}%",),
                        )
                        matches = cur.fetchall()

                        if not matches:
                            print("No matching products found.")
                            continue

                        if len(matches) == 1:
                            product_id = matches[0][0]
                            print(
                                f"Matched Product: {matches[0][1]} (ID: {product_id})"
                            )
                        else:
                            print("Multiple matches found:")
                            for match in matches:
                                print(f"- ID: {match[0]}, Name: {match[1]}")
                            product_id = input(
                                "Enter the product ID of the desired match: "
                            ).strip()

                    # Check if the product already exists in the wishlist
                    with conn.cursor() as cur:
                        cur.execute(
                            'SELECT product_id FROM "Wish_List" WHERE wishlist_name = %s AND product_id = %s',
                            (wishlist_name, product_id),
                        )
                        if cur.fetchone():
                            print("You already have this product in your wishlist.")
                            continue

                    quantity = input(
                        "Enter the quantity (or type 'exit' to cancel): "
                    ).strip()
                    if quantity.lower() == "exit":
                        print("Operation canceled.")
                        continue
                    try:
                        quantity = int(quantity)
                    except ValueError:
                        print("Invalid quantity. Please enter a number.")
                        continue

                    with conn.cursor() as cur:
                        cur.execute(
                            'INSERT INTO "Wish_List" (wishlist_name, product_id, number, owned) VALUES (%s, %s, %s, FALSE)',
                            (wishlist_name, product_id, quantity),
                        )
                        conn.commit()
                    print("Item added successfully.")
                elif choice == "4":
                    product_id = input(
                        "Enter the product ID to remove (or type 'exit' to cancel): "
                    ).strip()
                    if product_id.lower() == "exit":
                        print("Operation canceled.")
                        continue

                    # Validate product ID
                    with conn.cursor() as cur:
                        cur.execute(
                            'SELECT product_id FROM "Wish_List" WHERE wishlist_name = %s AND product_id = %s',
                            (wishlist_name, product_id),
                        )
                        if not cur.fetchone():
                            print(
                                f"Product ID {product_id} does not exist in the wishlist '{wishlist_name}'."
                            )
                            continue

                    with conn.cursor() as cur:
                        cur.execute(
                            'DELETE FROM "Wish_List" WHERE wishlist_name = %s AND product_id = %s',
                            (wishlist_name, product_id),
                        )
                        conn.commit()
                    print("Item removed successfully.")

                elif choice == "5":
                    product_id = input(
                        "Enter the product ID to modify (or type 'exit' to cancel): "
                    ).strip()
                    if product_id.lower() == "exit":
                        print("Operation canceled.")
                        continue

                    # Validate product ID
                    with conn.cursor() as cur:
                        cur.execute(
                            'SELECT product_id FROM "Wish_List" WHERE wishlist_name = %s AND product_id = %s',
                            (wishlist_name, product_id),
                        )
                        if not cur.fetchone():
                            print(
                                f"Product ID {product_id} does not exist in the wishlist '{wishlist_name}'."
                            )
                            continue

                    quantity = input(
                        "Enter the new quantity (or type 'exit' to cancel): "
                    ).strip()
                    if quantity.lower() == "exit":
                        print("Operation canceled.")
                        continue
                    try:
                        quantity = int(quantity)
                    except ValueError:
                        print("Invalid quantity. Please enter a number.")
                        continue

                    with conn.cursor() as cur:
                        cur.execute(
                            'UPDATE "Wish_List" SET number = %s WHERE wishlist_name = %s AND product_id = %s',
                            (quantity, wishlist_name, product_id),
                        )
                        conn.commit()
                    print("Quantity updated successfully.")

                elif choice == "6":
                    product_id = input(
                        "Enter the product ID to modify ownership status (or type 'exit' to cancel): "
                    ).strip()
                    if product_id.lower() == "exit":
                        print("Operation canceled.")
                        continue
                    owned = (
                        input(
                            "Do you own this item? (yes/no or type 'exit' to cancel): "
                        )
                        .strip()
                        .lower()
                    )
                    if owned == "exit":
                        print("Operation canceled.")
                        continue
                    owned = owned == "yes"
                    with conn.cursor() as cur:
                        cur.execute(
                            'UPDATE "Wish_List" SET owned = %s WHERE wishlist_name = %s AND product_id = %s',
                            (owned, wishlist_name, product_id),
                        )
                        conn.commit()
                    print("Ownership status updated successfully.")
                elif choice == "7":
                    break
                else:
                    print("Invalid choice. Please try again.")


# Main Menu
"""
Function name: main_menu
Input: conn (Database connection object)
Output: None
Description: Provides the main menu for interacting with the application. 
    Offers options to view, add, or delete wishlists, and view items in a 
    wishlist.
"""


def main_menu(conn):
    while True:
        print("\n=== Bike Wishlist System ===")
        print("1. View All Wishlists")
        print("2. Add Wishlist")
        print("3. Remove Wishlist")
        print("4. View Wishlist Items")
        print("5. Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            wishlists = ListTracker.get_all_wishlists(conn)
            if wishlists:
                print("\nAvailable Wishlists:")
                for wl in wishlists:
                    print(f"- {wl.wishlist_name}")
            else:
                print("\nNo wishlists found.")
        elif choice == "2":
            wishlist_name = input(
                "Enter a unique wishlist name (or type 'exit' to cancel): "
            ).strip()
            if wishlist_name.lower() == "exit":
                print("Operation canceled.")
                continue
            ListTracker.createList(conn, wishlist_name)
        elif choice == "3":
            wishlists = ListTracker.get_all_wishlists(conn)
            if wishlists:
                print("\nAvailable Wishlists:")
                for wl in wishlists:
                    print(f"- {wl.wishlist_name}")
            else:
                print("\nNo wishlists available to remove.")
                continue

            wishlist_name = input(
                "Enter the wishlist name to remove (or type 'exit' to cancel): "
            ).strip()
            if wishlist_name.lower() == "exit":
                print("Operation canceled.")
                continue
            ListTracker.deleteList(conn, wishlist_name)
        elif choice == "4":
            wishlist_name = input(
                "Enter the wishlist name to view (or type 'exit' to cancel): "
            ).strip()
            if wishlist_name.lower() == "exit":
                print("Operation canceled.")
                continue
            ListTracker.viewList(conn, wishlist_name)
        elif choice == "5" or choice == "exit":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


# Main - Program run
if __name__ == "__main__":
    attempts = 3
    conn = None
    while attempts > 0:
        password = get_password()
        conn = get_connection(password)
        if conn:
            break
        attempts -= 1
        print(f"Connection failed. You have {attempts} attempts remaining.")

    if not conn:
        print("Maximum attempts exceeded. Press any key to exit program...")
        getch()
        exit()

    main_menu(conn)