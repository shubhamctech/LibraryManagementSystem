import tkinter as tk
import sqlite3
import random

db_path = "LMS.db"  # Database path


class LibraryManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("800x640")
        
        # Establish database connection
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        
        # Output area
        self.output_label = None
        
        # Main menu UI
        self.create_main_menu()

    def create_main_menu(self):
        """Creates the main menu interface."""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        title = tk.Label(self.root, text="Library Management System", font=("Arial", 16))
        title.pack(pady=32)
        
        button_frame = tk.Frame(self.root)
        button_frame.pack()

        # Function buttons for tasks
        self.create_custom_button(button_frame, "1.", "Checkout Book", self.checkout_book_ui, 0)
        self.create_custom_button(button_frame, "2.", "Add New Borrower", self.add_borrower_ui, 1)
        self.create_custom_button(button_frame, "3.", "Add New Book", self.add_new_book_ui, 2)
        self.create_custom_button(button_frame, "4.", "Books Loaned by Branch", self.loaned_copies_ui, 3)
        self.create_custom_button(button_frame, "5.", "Late Book Returns in Range", self.late_returns_ui, 4)
        self.create_custom_button(button_frame, "6.a.", "Borrower Late Fee Info", self.borrower_info_ui, 5)
        self.create_custom_button(button_frame, "6.b.", "Book Late Fee Info", self.book_info_ui, 6)
        
        # Exit button
        exit_button = tk.Button(self.root, text="Exit", width=32, command=self.root.quit)
        exit_button.pack(pady=48)

    def create_custom_button(self, parent, bullet, text, command, row):
        """Creates a custom button with left-aligned bullet and centered text."""
        frame = tk.Frame(parent)
        frame.grid(row=row, column=0, padx=8, pady=4, sticky="ew")
        
        bullet_label = tk.Label(frame, text=bullet, anchor="w", width=4)
        bullet_label.pack(side="left")
        
        button = tk.Button(frame, text=text, command=command, anchor="center", width=24)
        button.pack(side="left", fill="x", expand=True)
    
    def create_input_ui(self, title, fields, submit_action):
        """Creates a form-like UI for inputting data."""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        title_label = tk.Label(self.root, text=title, font=("Arial", 14))
        title_label.pack(pady=10)
        
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)
        
        inputs = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(input_frame, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = tk.Entry(input_frame)
            entry.grid(row=i, column=1, padx=5, pady=5)
            inputs[key] = entry
            if i == 0:
                first_entry = entry 

        if first_entry:
            first_entry.focus_set()  # Set focus on the first entry widget
        
        submit_button = tk.Button(self.root, text="Submit", width=15, command=lambda: submit_action(inputs))
        submit_button.pack(pady=16)

        # Output area
        self.output_label = tk.Label(self.root, text="", font=("Arial", 12), wraplength=750, justify="left")
        self.output_label.pack()

        # Frame for table grid
        self.output_frame = tk.Frame(self.root)
        self.output_frame.pack(fill="both")
        
        back_button = tk.Button(self.root, text="Back to Menu", width=15, command=self.create_main_menu)
        back_button.pack(pady=32)
    
    def display_output(self, message):
        """Displays output below the input form."""
        if self.output_label:
            self.output_label.config(text=message)

    def display_table_in_grid(self, columns, rows):
        """Displays the table in a Tkinter grid."""
        # Clear any previous output in the grid
        for widget in self.output_frame.winfo_children():
            widget.destroy()

        # Create header row
        for col_index, col_name in enumerate(columns):
            header_label = tk.Label(self.output_frame, text=col_name, font=("Arial", 12, "bold"), relief="solid", width=20, anchor="w")
            header_label.grid(row=0, column=col_index, sticky="nsew")

        # Add rows of data
        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                value_label = tk.Label(self.output_frame, text=str(value), font=("Arial", 12), relief="solid", width=20, anchor="w")
                value_label.grid(row=row_index + 1, column=col_index, sticky="nsew")

        # Configure grid expansion
        for col_index in range(len(columns)):
            self.output_frame.grid_columnconfigure(col_index, weight=1)

        # Pack the output frame without expanding
        self.output_frame.pack(anchor="center")


    # Task functionalities
    def checkout_book_ui(self):
        """UI for checking out a book."""
        self.create_input_ui(
            "Checkout Book",
            [("Book ID:", "book_id"), ("Branch ID:", "branch_id"), ("Card Number:", "card_no")],
            self.checkout_book_action
        )
    
    def checkout_book_action(self, inputs):
        """Handles book checkout."""
        try:
            book_id = inputs["book_id"].get()
            branch_id = inputs["branch_id"].get()
            card_no = inputs["card_no"].get()

            # Check if the card_no exists in the BORROWER table (user is registered)
            self.cursor.execute("SELECT 1 FROM BORROWER WHERE Card_No = ?", (card_no,))
            borrower = self.cursor.fetchone()
            
            if not borrower:
                raise Exception(f"Borrower with Card Number '{card_no}' is not registered in the system.")

            # Check if the book is available in the specified branch
            self.cursor.execute("""
                SELECT No_Of_Copies FROM BOOK_COPIES WHERE Book_ID = ? AND Branch_ID = ?
            """, (book_id, branch_id))
            result = self.cursor.fetchone()

            # If the book doesn't exist or there are no copies, raise an error
            if not result or result[0] <= 0:
                raise Exception("No available copies of this book in the selected branch.")
            
            # Create the trigger if not exists
            self.cursor.execute("""
                        CREATE TRIGGER IF NOT EXISTS update_book_copies_after_checkout
                        AFTER INSERT ON BOOK_LOANS
                        FOR EACH ROW
                        BEGIN
                            UPDATE BOOK_COPIES
                            SET No_Of_Copies = No_Of_Copies - 1
                            WHERE Book_Id = NEW.Book_Id AND Branch_Id = NEW.Branch_Id;
                        END;
                    """)
            
            # Insert into BOOK_LOANS
            self.cursor.execute("""
                        INSERT INTO BOOK_LOANS (Book_ID, Branch_ID, Card_No, Date_Out, Due_Date, Returned_Date)
                        VALUES (?, ?, ?, DATE('now'), DATE('now', '+7 days'), "NULL")
                    """, (book_id, branch_id, card_no))
            
            # Commit the changes
            self.connection.commit()
            

            # Display the formatted table
            self.display_output("Book checked out successfully.\n\nUpdated Book Copies:\n\n")
           
            # Fetch column names
            self.cursor.execute("PRAGMA table_info(BOOK_COPIES);")
            columns = [column[1] for column in self.cursor.fetchall()]

            # Fetch rows from the BOOK_COPIES table for the specific Book_ID
            self.cursor.execute("SELECT * FROM BOOK_COPIES WHERE Book_ID = ? AND Branch_Id = ?", (book_id, branch_id))
            rows = self.cursor.fetchall()

            # Show updated BOOK_COPIES in a grid
            self.display_table_in_grid(columns, rows)
        except Exception as e:
            self.display_output(f"Error: {e}")
    

    def add_borrower_ui(self):
        """UI for adding a new borrower."""
        self.create_input_ui(
            "Add New Borrower",
            [("Borrower Name:", "name"), ("Address:", "address"), ("Phone Number:", "phone")],
            self.add_borrower_action
        )

    def add_borrower_action(self, inputs):
        """Handles adding a new borrower with a unique Card_No."""
        try:
            name = inputs["name"].get()
            address = inputs["address"].get()
            phone = inputs["phone"].get()

            # Check if a borrower with the exact same name, address, and phone already exists
            self.cursor.execute("""
                SELECT 1 FROM BORROWER WHERE Name = ? AND Address = ? AND Phone = ?
            """, (name, address, phone))
            if self.cursor.fetchone():
                raise Exception("A borrower with the same name, address, and phone already exists.")

            # Generate a unique Card_No
            while True:
                card_no = random.randint(100000, 999999)
                # Check if the Card_No already exists in the BORROWER table
                self.cursor.execute("SELECT 1 FROM BORROWER WHERE Card_No = ?", (card_no,))
                if not self.cursor.fetchone():  # If no matching row is found, it's unique
                    break  # Exit the loop if the Card_No is unique

            # Insert into BORROWER table with the unique Card_No
            self.cursor.execute("""
                INSERT INTO BORROWER (Card_No, Name, Address, Phone)
                VALUES (?, ?, ?, ?)
            """, (card_no, name, address, phone))
            
            # Commit the transaction
            self.connection.commit()
            
            # Display success message
            self.display_output(f"New borrower added successfully.\nCard Number: {card_no}\n")
            
            # Fetch column names for the BORROWER table
            self.cursor.execute("PRAGMA table_info(BORROWER);")
            columns = [column[1] for column in self.cursor.fetchall()]
            
            # Fetch the row we just inserted (using the Card_No to retrieve it)
            self.cursor.execute("SELECT * FROM BORROWER WHERE Card_No = ?", (card_no,))
            row = self.cursor.fetchone()
            
            # Show the new borrower's information in a grid
            self.display_table_in_grid(columns, [row])

        except Exception as e:
            self.display_output(f"Error: {e}")


    def add_new_book_ui(self):
        """UI for adding a new book."""
        self.create_input_ui(
            "Add New Book",
            [("Book Title:", "title"), ("Publisher:", "publisher"), ("Author:", "author"), ("Number of Copies:", "num_copies")],
            self.add_new_book_action
        )

    def add_new_book_action(self, inputs):
        """Handles adding a new book with publisher and author info, and updating copies in all branches."""
        try:
            # Get input values from user
            title = inputs["title"].get()
            publisher = inputs["publisher"].get()
            author = inputs["author"].get()
            num_copies = int(inputs["num_copies"].get())

            # Check if the book already exists in the BOOK table
            self.cursor.execute("""
                SELECT Book_Id FROM BOOK WHERE Title = ? AND Publisher_Name = ?
            """, (title, publisher))
            book = self.cursor.fetchone()

            # If book exists, get its Book_Id, otherwise create a new Book_Id
            if book:
                book_id = book[0]
            else:
                # Generate a new Book_Id (increment the last Book_Id)
                self.cursor.execute("SELECT MAX(Book_Id) FROM BOOK")
                last_book_id = self.cursor.fetchone()[0]
                book_id = last_book_id + 1 if last_book_id else 1  # If no books exist, start from 1

                # Insert into BOOK table
                self.cursor.execute("""
                    INSERT INTO BOOK (Book_Id, Title, Publisher_Name) 
                    VALUES (?, ?, ?)
                """, (book_id, title, publisher))

                # Insert into BOOK_AUTHORS table
                self.cursor.execute("""
                    INSERT INTO BOOK_AUTHORS (Book_Id, Author_Name)
                    VALUES (?, ?)
                """, (book_id, author))

            # Fetch all Branch_Id values from LIBRARY_BRANCH
            self.cursor.execute("SELECT Branch_Id FROM LIBRARY_BRANCH")
            branch_ids = [branch[0] for branch in self.cursor.fetchall()]

            # Loop through each branch and check if the Book-Branch combination exists in BOOK_COPIES
            for branch_id in branch_ids:
                self.cursor.execute("""
                    SELECT 1 FROM BOOK_COPIES WHERE Book_Id = ? AND Branch_Id = ?
                """, (book_id, branch_id))
                if self.cursor.fetchone():  # If combination exists, update No_Of_Copies
                    self.cursor.execute("""
                        UPDATE BOOK_COPIES
                        SET No_Of_Copies = No_Of_Copies + ?
                        WHERE Book_Id = ? AND Branch_Id = ?
                    """, (num_copies, book_id, branch_id))
                else:  # If combination doesn't exist, insert a new row
                    self.cursor.execute("""
                        INSERT INTO BOOK_COPIES (Book_Id, Branch_Id, No_Of_Copies)
                        VALUES (?, ?, ?)
                    """, (book_id, branch_id, num_copies))

            # Commit the transaction
            self.connection.commit()

            # Output success message
            self.display_output(f"Book '{title}' added successfully to all branches.\n")

            # Fetch column names for BOOK_COPIES
            self.cursor.execute("PRAGMA table_info(BOOK_COPIES);")
            book_copies_columns = [column[1] for column in self.cursor.fetchall()]

            # Insert 'Book_Title' at index 1 in the column list (after Book_Id)
            columns = [book_copies_columns[0]] + ['Book_Title'] + book_copies_columns[1:]

            # Fetch rows from BOOK_COPIES for the specific Book_Id
            self.cursor.execute("""
                SELECT bc.Book_Id, b.Title, bc.Branch_Id, bc.No_Of_Copies
                FROM BOOK_COPIES bc
                JOIN BOOK b ON bc.Book_Id = b.Book_Id
                WHERE bc.Book_Id = ?
            """, (book_id,))
            rows = self.cursor.fetchall()

            # Show updated BOOK_COPIES in a grid
            self.display_table_in_grid(columns, rows)

        except Exception as e:
            self.display_output(f"Error: {e}")


    
    def loaned_copies_ui(self):
        """UI for listing loaned copies per branch."""
        self.create_input_ui(
            "Books Loaned by Branch",
            [("Book Title:", "title")],
            self.loaned_copies_action
        )
    
    def loaned_copies_action(self, inputs):
        """Handles displaying the number of copies loaned out per branch for a given book title."""
        try:
            # Get the book title from user input
            title = inputs["title"].get().strip()

            if not title:
                raise Exception("Book title cannot be empty.")

            # Fetch the Book_Id for the given title
            self.cursor.execute("SELECT Book_Id FROM BOOK WHERE Title = ?", (title,))
            book = self.cursor.fetchone()
            if not book:
                raise Exception(f"No book found with the title '{title}'.")

            book_id = book[0]

            # Query to get the number of copies loaned out per branch
            self.cursor.execute("""
                SELECT BL.Branch_Id, LB.Branch_Name, COUNT(*) AS Num_Of_Books_Loaned
                FROM BOOK_LOANS BL
                INNER JOIN LIBRARY_BRANCH LB ON BL.Branch_Id = LB.Branch_Id
                WHERE BL.Book_Id = ? AND BL.Returned_Date IS "NULL"
                GROUP BY BL.Branch_Id, LB.Branch_Name
            """, (book_id,))

            rows = self.cursor.fetchall()
            if not rows:
                raise Exception(f"No branch has any copies of the book '{title}' currently loaned out.")

            # Define the column headers
            columns = ["Branch_Id", "Branch_Name", "Num_Of_Books_Loaned"]

            # Display the grid with the results
            self.display_output(f"Loaned Copies Per Branch for '{title}':\n\n")
            self.display_table_in_grid(columns, rows)

        except Exception as e:
            self.display_output(f"Error: {e}")


    def late_returns_ui(self):
        """UI for listing late returns."""
        self.create_input_ui(
            "Late Book Returns in Range",
            [("Start Due Date (YYYY-MM-DD):", "start_date"), ("End Due Date (YYYY-MM-DD):", "end_date")],
            self.late_returns_action
        )

    def late_returns_action(self, inputs):
        """Handles displaying late returns within a date range."""
        try:
            start_date = inputs["start_date"].get().strip()
            end_date = inputs["end_date"].get().strip()

            if not start_date or not end_date:
                raise Exception("Start and end due dates cannot be empty.")

            # Query to get late returns within the specified date range
            self.cursor.execute("""
                SELECT Book_Id, Branch_Id, Card_No, Date_Out, Due_Date, Returned_Date,
                       CAST(julianday(Returned_Date) - julianday(Due_Date) AS INTEGER) AS Late_Days
                FROM BOOK_LOANS
                WHERE Returned_Date > Due_Date AND Returned_Date IS NOT "NULL" AND Due_Date BETWEEN ? AND ?
            """, (start_date, end_date))

            rows = self.cursor.fetchall()
            if not rows:
                raise Exception("No late returns found for the specified due date range.")

            # Define the column headers
            columns = ["Book_Id", "Branch_Id", "Card_No", "Date_Out", "Due_Date", "Returned_Date", "Late_Days"]

            # Display the grid with the results
            self.display_output(f"Late Returns between {start_date} and {end_date}:\n\n")
            self.display_table_in_grid(columns, rows)

        except Exception as e:
            self.display_output(f"Error: {e}")

    def borrower_info_ui(self):
        """UI for borrower info with late fees."""
        self.create_input_ui(
            "Borrower Late Fee Info",
            [("Borrower ID (Card Number):", "borrower_id"), ("Borrower Name:", "borrower_name")],
            self.borrower_info_action
        )
    
    def borrower_info_action(self, inputs):
        """Handles querying late fees based on borrower filters."""
        try:
            # Get user inputs
            borrower_id = inputs["borrower_id"].get().strip()
            borrower_name = inputs["borrower_name"].get().strip()

            # Determine filters based on user input
            borrower_id = borrower_id if borrower_id else None
            borrower_name = borrower_name if borrower_name else None

            # Query the view with dynamic filters
            self.cursor.execute("""
                SELECT
                    Card_No AS Borrower_ID,
                    Borrower_Name,
                    CASE
                        WHEN LateFeeBalance IS NULL OR LateFeeBalance = 0 THEN '$0.00'
                        ELSE '$' || printf('%.2f', LateFeeBalance)
                    END AS LateFeeBalance
                FROM vBookLoanInfo
                WHERE
                    (Card_No = ? OR ? IS NULL)
                    AND (Borrower_Name LIKE '%' || ? || '%' OR ? IS NULL)
                ORDER BY
                    LateFeeBalance DESC;
            """, (borrower_id, borrower_id, borrower_name, borrower_name))

            rows = self.cursor.fetchall()

            # Check if results exist
            if not rows:
                raise Exception("No borrowers found matching the criteria.")

            # Define the column headers
            columns = ["Borrower_ID", "Borrower_Name", "LateFeeBalance"]

            # Display the grid with the results
            self.display_output("Late Fee Balances:\n\n")
            self.display_table_in_grid(columns, rows)

        except Exception as e:
            self.display_output(f"Error: {e}")


    def book_info_ui(self):
        """UI for querying book information based on borrower ID and other criteria."""
        self.create_input_ui(
            "Book Late Fee Info",
            [("Borrower ID (Card Number):", "borrower_id"), ("Book ID:", "book_id"), ("Book Title:", "book_title")],
            self.book_info_action
        )
    
    def book_info_action(self, inputs):
        """Handles querying book information based on borrower ID, book title, or book ID."""
        try:
            # Get user inputs
            borrower_id = inputs["borrower_id"].get().strip()
            book_id = inputs["book_id"].get().strip() if inputs["book_id"].get().strip() else None
            book_title = inputs["book_title"].get().strip()

            # Handle empty inputs
            borrower_id = borrower_id if borrower_id else None
            book_title = book_title if book_title else None

            # If book_id is provided, retrieve the corresponding Book_Title
            if book_id:
                self.cursor.execute("SELECT Title FROM BOOK WHERE Book_Id = ?", (book_id,))
                book_row = self.cursor.fetchone()
                if not book_row:
                    raise Exception(f"No book found with Book_Id '{book_id}'.")
                
                db_book_title = book_row[0]

                # If user provided book_title, check if it is a substring of the one from the BOOK table
                if book_title and book_title.lower() not in db_book_title.lower():
                    raise Exception(f"The provided Book_Title '{book_title}' does not match the title associated with Book_Id '{book_id}'.")
                
                # If no book_title provided, use the one from the database
                book_title = db_book_title

            # Execute the SQL query
            self.cursor.execute("""
                SELECT
                    v.Card_No AS Borrower_ID,
                    b.Book_Id,
                    v.Book_Title,
                    CASE
                        WHEN v.LateFeeBalance IS NULL THEN 'Non-Applicable'
                        ELSE '$' || printf('%.2f', v.LateFeeBalance)
                    END AS LateFeeAmount
                FROM vBookLoanInfo v
                JOIN BOOK b ON v.Book_Title = b.Title
                WHERE
                    (v.Card_No = ? OR ? IS NULL)
                    AND (v.Book_Title LIKE '%' || ? || '%' OR ? IS NULL)
                    AND (? IS NULL OR b.Book_Id = ?)
                ORDER BY
                    v.LateFeeBalance DESC;
            """, (borrower_id, borrower_id, book_title, book_title, book_id, book_id))

            # Fetch the results
            rows = self.cursor.fetchall()

            # Check if any records are found
            if not rows:
                raise Exception("No books found matching the criteria.")

            # Define column headers
            columns = ["Borrower_ID", "Book_ID", "Book_Title", "LateFeeAmount"]

            # Display results
            self.display_output("Book Information:\n\n")
            self.display_table_in_grid(columns, rows)

        except Exception as e:
            self.display_output(f"Error: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryManagementSystem(root)
    root.mainloop()
    