import sqlalchemy
import pyodbc
import google.generativeai as genai
import os

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
            if schema.startswith('sys') or schema in ['INFORMATION_SCHEMA', 'guest']:
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
    Executes a SQL query and formats the results as a table.
    
    Args:
        connection_string (str): The SQLAlchemy connection string.
        query (str): The T-SQL query to execute.
    
    Returns:
        tuple: A tuple containing the formatted results and any errors.
    """
    print("In execute_sql_query")
    query = query.replace('`', '').replace('sql','')
    try:
        engine = sqlalchemy.create_engine(connection_string)
        with engine.connect() as connection:
            result = connection.execute(sqlalchemy.text(query))
            
            if result.returns_rows:
                # Get column names
                columns = list(result.keys())
                
                # Fetch all rows
                rows = result.fetchall()
                
                # Format the output
                output = ""
                
                # Print the header row
                header = "|".join([f"{col:^20}" for col in columns])
                separator = "-" * len(header)
                output += f"{separator}\n"
                output += f"{header}\n"
                output += f"{separator}\n"
                
                # Print each data row
                for row in rows:
                    row_data = "|".join([f"{str(value):^20}" for value in row])
                    output += f"{row_data}\n"
                
                output += separator
                
                return output, None
            else:
                return f"Query executed successfully. Rows affected: {result.rowcount}", None
    except Exception as e:
        return None, f"Error executing the query: {e}"

def interactive_sql_agent(server_connection_str, gemini_api_key):
    """
    Runs the agentic AI in an interactive loop, prompting the user for questions.
    
    Args:
        server_connection_str (str): The SQL Server connection string.
        gemini_api_key (str): Your Gemini API key.
    """
    print("Welcome to the Interactive SQL Agent!")
    print("Type 'exit' or 'quit' to end the session.")
    
    # Introspect the database once at the beginning
    print("\nPerceiving the database schema...")
    schema = get_schema_info(server_connection_str)
    
    if "Error" in schema:
        print(f"Failed to load database schema: {schema}")
        return
        
    print("Schema loaded successfully. Ready to answer your questions.")
    
    while True:
        user_question = input("\nYour question (or 'exit'/'quit'): ").strip()
        
        # Check for exit command
        if user_question.lower() in ['exit', 'quit']:
            print("Exiting session. Goodbye!")
            break
            
        if not user_question:
            continue
            
        print("Generating a SQL query with Gemini...")
        query = generate_sql_query(user_question, schema, gemini_api_key)
        
        if "Error" in query:
            print(f"Query generation failed. Reason: {query}")
            continue
            
        print(f"\nGenerated Query: \n{query}")
        
        print("\nExecuting the query...")
        results, error = execute_sql_query(server_connection_str, query)
        
        if error:
            print(f"Query failed. Reason: {error}")
        else:
            print(f"\nQuery successful. Results:\n{results}")

# --- To use the agent ---

# #question = "How many customers are in the Customers table?"
# question = "What are my top 10 customers for total sales in 1998 and parse json into rows."

# final_result = sql_agent(question, my_connection_string, my_api_key)
# --- To use the interactive agent ---
database = input("Enter database name:")
my_api_key=os.environment["AI_API_KEY"]
sqllogin = os.environment["SQLLOGIN"]
sqlpwd = os.environment["SQLPWD"]

# Example connection string for SQL Server with pyodbc
# This assumes you have the appropriate ODBC driver installed
connection_str = f"mssql+pyodbc://{sqllogin}:{sqlpwd}/{database}?driver=ODBC+Driver+17+For+SQL+Server"

my_connection_string = f"mssql+pyodbc://{sqllogin}:{sqlpwd}/{database}?driver=ODBC+Driver+17+For+SQL+Server"

interactive_sql_agent(my_connection_string, my_api_key)

# print("\n--- Final Result ---")
# print(final_result)

