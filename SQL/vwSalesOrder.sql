USE AdventureWorks2022;
GO

CREATE VIEW Sales.vwSalesOrder AS 
SELECT soh.*,
       p.FirstName,
       p.LastName 
FROM Sales.SalesOrderHeader soh
JOIN Sales.Customer c ON soh.CustomerID = c.CustomerID
JOIN Person.Person p ON c.PersonID = p.BusinessEntityID;
GO
