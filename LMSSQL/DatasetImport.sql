-- shubham@Shubhams-MacBook-Pro LibraryManagementSystem % sqlite3 LMS.db < LMSSQL/CreateTable.sql
-- shubham@Shubhams-MacBook-Pro LibraryManagementSystem % sqlite3 LMS.db                    
-- SQLite version 3.43.2 2023-10-10 13:08:14
-- Enter ".help" for usage hints.
sqlite> .mode csv
sqlite> .import -skip 1 LMSDataset/Publisher.csv PUBLISHER
sqlite> .import -skip 1 LMSDataset/Book.csv BOOK
sqlite> .import -skip 1 LMSDataset/Book_Authors.csv BOOK_AUTHORS
sqlite> .import -skip 1 LMSDataset/Library_Branch.csv LIBRARY_BRANCH
sqlite> .import -skip 1 LMSDataset/Book_Copies.csv BOOK_COPIES
sqlite> .import -skip 1 LMSDataset/Borrower.csv BORROWER
sqlite> .import -skip 1 LMSDataset/Book_Loans.csv BOOK_LOANS
sqlite> SELECT 'PUBLISHER' AS Table_Name, COUNT(*) AS Record_Count FROM PUBLISHER
   ...> UNION SELECT 'BOOK', COUNT(*) FROM BOOK
   ...> UNION SELECT 'BOOK_AUTHORS', COUNT(*) FROM BOOK_AUTHORS
   ...> UNION SELECT 'LIBRARY_BRANCH', COUNT(*) FROM LIBRARY_BRANCH
   ...> UNION SELECT 'BOOK_COPIES', COUNT(*) FROM BOOK_COPIES
   ...> UNION SELECT 'BORROWER', COUNT(*) FROM BORROWER
   ...> UNION SELECT 'BOOK_LOANS', COUNT(*) FROM BOOK_LOANS;
-- BOOK,21
-- BOOK_AUTHORS,21
-- BOOK_COPIES,21
-- BOOK_LOANS,21
-- BORROWER,21
-- LIBRARY_BRANCH,3
-- PUBLISHER,17