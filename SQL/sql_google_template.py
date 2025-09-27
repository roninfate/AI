import sqlalchemy
import pyodbc
import google.generativeai as genai
import os


###############################################################################################
# Insert functions here

###############################################################################################



###############################################################################################
#Main processing section

###############################################################################################

sqlserver = input("Enter SQL Server name:")
database = input("Enter database name:")
my_api_key=os.environ["AI_API_KEY"]
sqllogin = os.environ["SQLLOGIN"]
sqlpwd = os.environ["SQLPWD"]

# Example connection string for SQL Server with pyodbc
# This assumes you have the appropriate ODBC driver installed
#connection_str = f"mssql+pyodbc://{sqllogin}:{sqlpwd}/{database}?driver=ODBC+Driver+17+For+SQL+Server"

my_connection_string = f"mssql+pyodbc://{sqllogin}:{sqlpwd}@{sqlserver}/{database}?driver=ODBC+Driver+17+For+SQL+Server"

interactive_sql_agent(my_connection_string, my_api_key)