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

# ==========OLLAMA HELPERS==========
def ask_ollama(prompt, model="llama3"):
    """Send a prompt to Ollama and return response text."""
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"].strip().replace("`","")

def generate_sql(question, schema_context=None):
    """Ask Ollama to generate T-SQL from natural language"""
    prompt = f"""
    You are an expert SQL Server assistant.
    Convert this question into a valid T-SQL query.
    Output only SQL, no explanation.

    Question: {question}
    Tables: {schema_context if schema_context else "General database schema"}
    """
    return ask_ollama(prompt)

def fix_sql(error_msg, sql, schema_context=None):
    """Ask Ollama to fix SQL given an error message."""

    prompt = f"""
    The following SQL failed in SQL Server:

    {sql}

    Error: {error_msg}

    Please providew a corrected SQL query.  Only output SQL.
    Tables: {schema_context if schema_context else "General database schema"}
    """
    return ask_ollama(prompt)

def explain_results(question, df):
    # Ask Ollama to explain results in plain Engish.
    # Limit data preview to avoid huge prompt
    preview = df.head(10).to_string(index=False)

    prompt = f"""
    You asked: {question}

    Here are the first rows of the SQL Server result:
    {preview}

    Please summarize what this means in plain English.
    """

    return ask_ollama(prompt)

# ========== MAIN AGENT FUNCTION ##########
def agent_query(question, schema_context=None, retries=5):

    sql = generate_sql(question, schema_context)
    for attempt in range(retries):
        try:
            df = pd.read_sql(sql, conn)
            explanation = explain_results(question, df)
            return sql, df, explanation
        except Exception as e:
            print(f"SQL failed (attempt {attempt+1}): {e}")
            sql = fix_sql(str(e), sql, schema_context)
    raise RuntimeError("Query failed after retries.")

# ========== EXAMPLE USAGE ##########
if __name__ == "__main__":
    # Natural language question
    question = "Show me the top 5 customers by total sales in 2014"

    # Optionalschema hint
    schema_context = """
    Sales.vwSalesOrder(SalesOrderID, CustomerID, OrderDate, TotalDue, FirstName, LastName)
    """

    sql, df, explanation = agent_query(question, schema_context)

    print("\nGenerated SQL:\n", sql)
    print("\nQuery Results:\n")
    print(df.head())
    print("\nAI Explanation:\n", explanation)

