import os
import pyodbc
import pandas as pd 
import ollama

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

