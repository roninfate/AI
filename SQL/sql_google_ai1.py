import sqlalchemy
import pyodbc
import google.generativeai as genai

def get_schema_info(connection_string):
    """
    Connects to a SQL Server database and retrieves schema information for all schemas.
    
    Args:
        connection_string (str): The SQLAlchemy connection string.
    
    Returns:
        str: A formatted string of the database schema.
    """
    try:
        engine = sqlalchemy.create_engine(connection_string)
        inspector = sqlalchemy.inspect(engine)
        
        # Get all schemas in the database
        schemas = inspector.get_schema_names()
        
        schema_info = "The database contains the following tables and their columns, organized by schema:\n"
        
        for schema in schemas:
            # Skip system schemas that start with 'db_' or 'sys'
            if schema.startswith('db_') or schema.startswith('sys') or schema in ['INFORMATION_SCHEMA', 'guest']:
                continue
                
            tables = inspector.get_table_names(schema=schema)
            if tables:
                schema_info += f"\n--- Schema: {schema} ---\n"
                for table in tables:
                    schema_info += f"  - Table: {table}\n"
                    columns = inspector.get_columns(table, schema=schema)
                    for col in columns:
                        schema_info += f"    - {col['name']} ({col['type']})\n"
                
        return schema_info
    except Exception as e:
        return f"Error introspecting the database: {e}"

# Example connection string for SQL Server with pyodbc
# This assumes you have the appropriate ODBC driver installed
connection_str = "mssql+pyodbc://python:Trustno1%40all@localhost/AdventureWorks2022?driver=ODBC+Driver+17+For+SQL+Server"

def generate_sql_query(user_question, schema_info, api_key):
    """
    Uses the Gemini API to generate a SQL query based on a natural language question.
    
    Args:
        user_question (str): The natural language question from the user.
        schema_info (str): The string representation of the database schema.
        api_key (str): Your Gemini API key.
        
    Returns:
        str: The generated SQL query.
    """
    print("In generate_sql_query")

    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    You are an AI assistant that translates natural language to T-SQL queries for a SQL Server database.
    
    Here is the schema of the database you are working with:
    {schema_info}
    
    Your task is to generate a single, valid T-SQL query that answers the following question. Do not include any extra text, explanations, or markdown. Just provide the query itself.

    Question: {user_question}
    
    T-SQL Query:
    """
    
    try:
        response = model.generate_content(prompt)
        # Assuming the model returns the query as a string.
        query = response.text.strip()
        return query
    except Exception as e:
        return f"Error generating query with Gemini API: {e}"

def execute_sql_query(connection_string, query):
    """
    Executes a SQL query against a SQL Server database.
    
    Args:
        connection_string (str): The SQLAlchemy connection string.
        query (str): The T-SQL query to execute.
    
    Returns:
        tuple: A tuple containing the results and any errors.
    """
    print("In execute_sql_query")
    try:
        engine = sqlalchemy.create_engine(connection_string)
        with engine.connect() as connection:
            result = connection.execute(sqlalchemy.text(query))
            if result.returns_rows:
                # Fetch all rows if the query returns data
                rows = result.fetchall()
                return rows, None
            else:
                # For non-SELECT queries (e.g., INSERT, UPDATE), return success
                return f"Query executed successfully. Rows affected: {result.rowcount}", None
    except Exception as e:
        return None, f"Error executing the query: {e}"

def sql_agent(user_question, server_connection_str, gemini_api_key):
    """
    Main function for the agentic AI.
    
    Args:
        user_question (str): The natural language question.
        server_connection_str (str): The SQL Server connection string.
        gemini_api_key (str): Your Gemini API key.
    
    Returns:
        str: The result of the query or an error message.
    """
    print("1. Perceiving the database schema...")
    print(server_connection_str)

    schema = get_schema_info(server_connection_str)
    
    if "Error" in schema:
        return schema
        
    print("2. Generating a SQL query with Gemini...")
    query = generate_sql_query(user_question, schema, gemini_api_key)
    
    if "Error" in query:
        return query
        
    print(f"Generated Query: \n{query}")
    
    print("3. Executing the query...")
    results, error = execute_sql_query(server_connection_str, query)
    
    if error:
        # Here you could implement a more sophisticated agentic loop
        # by sending the error back to Gemini for correction.
        # For simplicity, we'll just return the error.
        return f"Query failed. Reason: {error}"
    else:
        return f"Query successful. Results:\n{results}"

# --- To use the agent ---
my_api_key = 'AIzaSyDMt2oRAXpEDV-Hip4wjCNfcinq7dsJNo4'
my_connection_string = "mssql+pyodbc://python:Trustno1%40all@localhost/AdventureWorks2022?driver=ODBC+Driver+17+For+SQL+Server"

question = "How many customers are in the Customers table?"

final_result = sql_agent(question, my_connection_string, my_api_key)
print("\n--- Final Result ---")
print(final_result)

