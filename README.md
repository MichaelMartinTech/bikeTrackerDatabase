# Bike Wishlist Command-Line Application for Database Interaction
**Author:** Michael R. Martin

**Initially Uploaded on GitHub: 12/12/2024**

## Purpose:  
This program is a Python-based command-line application for managing bike wishlists using a PostgreSQL database.
It is modeled on an external relational database, and includes additional custom tables for managing wishlists and their associated items.
The items included in the wishlists are sourced from the external dataset, while the wishlist structure and related functionality are custom-designed.
---

**Note:** This project is based on the schema of the Bike Store Relational Database from SQLServerTutorial.net.  
*Due to copyright restrictions, the actual dataset is not included. The code is intended solely for educational and archival purposes.*  
- **Data Reference:** [Bike Store Sample Database on Kaggle](https://www.kaggle.com/datasets/dillonmyrick/bike-store-sample-database?select=brands.csv)  
- **Original Source:** [SQL Server Tutorial: Bike Store Relational Database](https://www.sqlservertutorial.net/getting-started/sql-server-sample-database/)  

---

## Key Features:
1. **Secure Database Interaction**: Password-protected connection to ensure secure access and efficient error handling.
2. **Wishlist Management**: Add, view, and delete wishlists with checks for duplicate or missing names.
3. **Item Management**: Add, update, or remove items in a wishlist (Including quantity and ownership tracking.)
4. **Product Browsing**: View available products by category or as a full list, with detailed product information.
5. **Error Handling**: Provides clear error messages for invalid operations, enhancing user experience.

## How It Works:
- Users connect securely to the PostgreSQL database and navigate through a menu-driven interface.
- SQL queries manage data such as wishlists, products, and item details.
- The program ensures data integrity with validations for duplicate entries, invalid inputs, and user cancellations.

## Additional Notes:  
- The system is scalable, with potential for multi-user support and analytics. 
- This repository provides a foundational implementation of wishlist management with Python and PostgreSQL.

## Libraries and Tools Used

This project utilizes the following libraries and tools for securely connecting and interacting with a PostgreSQL database:
1. **`psycopg`**: A PostgreSQL adapter for Python, used to execute SQL queries, manage database transactions, and handle connections.
   - Ensures efficient communication between the Python application and the PostgreSQL database.
2. **`getpass`**: Library for securely prompting and handling password input from users.
   - Masks the password during input to maintain security.
3. **`msvcrt`** ``(Windows-only)``: Provides access to system-level utilities, specifically used here for handling keypress events without requiring the Enter key.
