import os
import pyodbc
import pandas as pd 
import ollama

import warnings

#warnings.filterwarnings('ignore', category=UserWarning, module='pandas.io.sql')

# --------------SQL Server Config ---------------
server = 'localhost'
database = 'AdventureWorks2022'
username = 'python'
password = 'Trustno1@all'
driver = '{ODBC Driver 17 for SQL Server}'

conn_str = f"""
DRIVER={driver};
SERVER={server};
DATABASE={database};
UID={username};
PWD={password};
"""

conn = pyodbc.connect(conn_str)

# ==========FUNCTION TO ASK OLLAMA==========
def nl_to_sql(question, table_context=None):
    """Send a natural language question to Ollama and get back T-SQL."""
    prompt = f"""
    You are a SQL Server assistant.
    Convert the following natural language question into a valid T-SQL query.
    Only output SQL (no explanation).

    Question: {question}

    Tables available:
    {table_context if table_context else "General SQL Server database."}
    """

    response = ollama.chat(model='llama3', messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"].strip()

# ==========FUNCTION TO RUN QUERY==========
def run_query(sql):
    """Run SQL query and retrun as pandas dataframe"""
    df = pd.read_sql(sql, conn)
    return df

# ==========EXAMPLE USAGE==========
if __name__ == "__main__":
    #Example: you ask in plain englist
    question = "Show me the top 5 customers by total sales in 2014."

    # (Optional) provide schema/table names for better sql generation
    table_context = "Sales.vwSalesOrder(SalesOrderID, CustomerID, OrderDate, TotalDue, FirstName, LastName)"

    sql = nl_to_sql(question, table_context)
    sql = sql.replace("`", "")

    print("Generated SQL:\n", sql)

    try:
        df = run_query(sql)
        print("\nQuery Results")
        print(df)
    except Exception as e:
        print("Error running query: ", e)

