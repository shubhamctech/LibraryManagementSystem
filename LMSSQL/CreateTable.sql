CREATE TABLE PUBLISHER (
    Publisher_Name TEXT PRIMARY KEY,
    Phone TEXT NOT NULL,
    Address TEXT
);

CREATE TABLE BOOK (
    Book_Id INTEGER PRIMARY KEY,
    Title TEXT NOT NULL,
    Publisher_Name TEXT NOT NULL,
    FOREIGN KEY (Publisher_Name) REFERENCES PUBLISHER(Publisher_Name)
);

CREATE TABLE BOOK_AUTHORS (
    Book_Id INTEGER,
    Author_Name TEXT,
    PRIMARY KEY (Book_Id, Author_Name),
    FOREIGN KEY (Book_Id) REFERENCES BOOK(Book_Id)
);

CREATE TABLE LIBRARY_BRANCH (
    Branch_Id INTEGER PRIMARY KEY,
    Branch_Name TEXT NOT NULL,
    Branch_Address TEXT
);

CREATE TABLE BOOK_COPIES (
    Book_Id INTEGER,
    Branch_Id INTEGER,
    No_Of_Copies INTEGER NOT NULL,
    PRIMARY KEY (Book_Id, Branch_Id),
    FOREIGN KEY (Book_Id) REFERENCES BOOK(Book_Id),
    FOREIGN KEY (Branch_Id) REFERENCES LIBRARY_BRANCH(Branch_Id)
);

CREATE TABLE BORROWER (
    Card_No INTEGER PRIMARY KEY,
    Name TEXT NOT NULL,
    Address TEXT,
    Phone TEXT NOT NULL
);

CREATE TABLE BOOK_LOANS (
    Book_Id INTEGER,
    Branch_Id INTEGER,
    Card_No INTEGER,
    Date_Out TEXT,
    Due_Date TEXT NOT NULL,
    Returned_Date TEXT,
    PRIMARY KEY (Book_Id, Branch_Id, Card_No, Date_Out),
    FOREIGN KEY (Book_Id) REFERENCES BOOK(Book_Id),
    FOREIGN KEY (Branch_Id) REFERENCES LIBRARY_BRANCH(Branch_Id),
    FOREIGN KEY (Card_No) REFERENCES BORROWER(Card_No)
);