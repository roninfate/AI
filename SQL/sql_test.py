import sqlalchemy
import pyodbc
import google.generativeai as genai
import os


if __name__ == "__main__":
    print("Hello")

    sqlserver = input("Enter SQL Server name:")
    database = input("Enter database name:")
    my_api_key=os.environ["AI_API_KEY"]
    sqllogin = os.environ["SQLLOGIN"]
    sqlpwd = os.environ["SQLPWD"]

    my_connection_string = f"mssql+pyodbc://{sqllogin}:{sqlpwd}@{sqlserver}/{database}?driver=ODBC+Driver+17+For+SQL+Server"

    interactive_sql_agent(my_connection_string, my_api_key)


def interactive_sql_agent(server_connection_str, api_key):
    """
    Runs the agentic AI in an interactive loop, prompting the user for questions.
    
    Args:
        server_connection_str (str): The SQL Server connection string.
        api_key (str): Your API key.
    """
    print("Welcome to the Interactive SQL Agent!")
    print("Type 'exit' or 'quit' to end the session.")


def get_schema_info(connection_string):
    """
    Connects to a SQL Server database and retrieves schema information for all schemas.
    
    Args:
        connection_string (str): The SQLAlchemy connection string.
    
    Returns:
        str: A formatted string of the database schema.
    """


def generate_sql_query(user_question, schema_info, api_key):
    """
    Uses the Gemini API to generate a SQL query based on a natural language question.
    
    Args:
        user_question (str): The natural language question from the user.
        schema_info (str): The string representation of the database schema.
        api_key (str): Your API key.
        
    Returns:
        str: The generated SQL query.
    """


def execute_sql_query(connection_string, query):
    """
    Executes a SQL query and formats the results as a table.
    
    Args:
        connection_string (str): The SQLAlchemy connection string.
        query (str): The T-SQL query to execute.
    
    Returns:
        tuple: A tuple containing the formatted results and any errors.
    """
    # There is a ` mark at the start and end of generated query.  In order to get the query to run, 
    # the tick marks have to be removed.
    query = query.replace('`', '').replace('sql','')

