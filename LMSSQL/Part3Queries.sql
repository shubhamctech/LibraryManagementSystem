-- Query 1: Add extra column ‘Late’ to BOOK_LOANS table.
-- Values will be 0 for non-late retuns, & 1 for late returns.
ALTER TABLE BOOK_LOANS ADD COLUMN late INTEGER DEFAULT 0;

UPDATE BOOK_LOANS
SET Late = CASE
	WHEN Returned_date > Due_date THEN 1
	ELSE 0
END;


-- Query 2: Add an extra column ‘LateFee’ to the Library_Branch table.
-- Decide late fee per day for each branch and update that column.
ALTER TABLE LIBRARY_BRANCH ADD COLUMN LateFee REAL DEFAULT 0;

UPDATE LIBRARY_BRANCH
SET LateFee = CASE
	WHEN Branch_ID = 1 THEN 1.00
	WHEN Branch_ID = 2 THEN 1.50
	WHEN Branch_ID = 3 THEN 2.00
	ELSE 0.50
END;


-- Query 3: Create a view vBookLoanInfo that retrieves all information per book loan.
CREATE VIEW vBookLoanInfo AS
SELECT
	B.Card_No,
	BR.Name As Borrower_Name,
	B.Date_Out,
	B.Due_Date,
	B.Returned_date,
    CAST((JulianDay(B.Returned_date)-JulianDay(B.Date_Out)) As INTEGER) AS TotalDays,
    BO.Title AS Book_Title,
    CASE
        WHEN B.Returned_date > B.Due_Date THEN
            CAST((JulianDay(B.Returned_date) – JulianDay(B.Due_Date)) AS INTEGER)
        ELSE 0
    END AS Days_Late,
    B.Branch_ID,
    CASE
        WHEN B.Returned_Date > B.Due_Date THEN
            (JulianDay(B.Returned_date) – JulianDay(B.Due_Date)) * LB.LateFee
        ELSE 0
    END AS LateFeeBalance
FROM BOOK_LOANS B
JOIN BORROWER BR ON B.CARD_NO = BR.CARD_NO
JOIN BOOK BO ON B.BOOK_ID = BO.BOOK_ID
JOIN LIBRARY_BRANCH LB ON B.BRANCH_ID = LB.BRANCH_ID;