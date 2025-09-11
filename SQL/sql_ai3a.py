import pyodbc
import pandas as pd
import ollama
import sys

# ========= SQL SERVER CONFIG =========
server = "localhost"
database = "AdventureWorks2022"
username = "python"
password = "Trustno1@all"
driver = "{ODBC Driver 17 for SQL Server}"

conn_str = f"""
DRIVER={driver};
SERVER={server};
DATABASE={database};
UID={username};
PWD={password};
"""
conn = pyodbc.connect(conn_str)

# ========= CHAT + SCHEMA MEMORY =========
chat_history = []
schema_cache = {}

# ========= STREAMING HELPER =========
def stream_ollama(prompt, role="user", model="llama3"):
    """Stream response from Ollama with conversation context."""
    global chat_history
    messages = chat_history + [{"role": role, "content": prompt}]
    reply = ""

    for chunk in ollama.chat(model=model, messages=messages, stream=True):
        if "message" in chunk and "content" in chunk["message"]:
            text = chunk["message"]["content"]
            reply += text
            sys.stdout.write(text)
            sys.stdout.flush()

    print()  # newline at end
    chat_history.append({"role": role, "content": prompt})
    chat_history.append({"role": "assistant", "content": reply})
    return reply.strip()

# ========= SCHEMA DISCOVERY =========
def get_schema(table_name=None):
    """Fetch schema info from SQL Server and cache it."""
    global schema_cache

    if table_name and table_name in schema_cache:
        return schema_cache[table_name]

    cursor = conn.cursor()
    if table_name:
        query = f"""
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, TABLE_SCHEMA
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = '{table_name}'
        ORDER BY ORDINAL_POSITION
        """
    else:
        query = """
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, TABLE_SCHEMA
        FROM INFORMATION_SCHEMA.COLUMNS
        ORDER BY TABLE_NAME, ORDINAL_POSITION
        """

    rows = cursor.execute(query).fetchall()
    df = pd.DataFrame(rows, columns=["Table", "Column", "Type"])

    for t in df["Table"].unique():
        schema_cache[t] = df[df["Table"] == t].to_dict(orient="records")

    return schema_cache if not table_name else schema_cache[table_name]

def format_schema(schema_dict):
    """Format schema cache into text for the LLM."""
    formatted = []
    for table, cols in schema_dict.items():
        col_list = ", ".join([f"{c['Column']}({c['Type']})" for c in cols])
        formatted.append(f"{table}({col_list})")
    return "\n".join(formatted)

# ========= SQL HELPERS =========
def generate_sql(question):
    schema_text = format_schema(schema_cache) if schema_cache else "Unknown schema"
    prompt = f"""
    Convert this question into a valid T-SQL query for SQL Server.
    Only return SQL code, no explanations.

    Question: {question}
    Schema:
    {schema_text}
    """
    return stream_ollama(prompt)

def fix_sql(error_msg, sql):
    schema_text = format_schema(schema_cache) if schema_cache else "Unknown schema"
    prompt = f"""
    The following SQL failed in SQL Server:

    {sql}

    Error: {error_msg}

    Fix the query. Only return corrected SQL code.
    Schema:
    {schema_text}
    """
    return stream_ollama(prompt)

def explain_results(question, df):
    preview = df.head(10).to_string(index=False)
    prompt = f"""
    You asked: {question}

    Here are the first rows of the result:
    {preview}

    Summarize this in plain English.
    """
    return stream_ollama(prompt)

# ========= MAIN AGENT =========
def agent_query(question, retries=2):
    sql = generate_sql(question)

    for attempt in range(retries):
        try:
            df = pd.read_sql(sql, conn)
            explanation = explain_results(question, df)
            return sql, df, explanation
        except Exception as e:
            print(f"\n⚠️ SQL failed (attempt {attempt+1}): {e}")

            # If it's a schema-related error, refresh schema
            if "Invalid object name" in str(e) or "Invalid column name" in str(e):
                print("🔎 Refreshing schema from INFORMATION_SCHEMA...")
                get_schema()

            print("🤖 Trying to fix query...")
            sql = fix_sql(str(e), sql)

    raise RuntimeError("Query failed after retries.")

# ========= CHAT LOOP =========
if __name__ == "__main__":
    print("💬 Schema-Aware Streaming SQL Agent — type 'exit' to quit")

    # Load schema at startup
    print("🔎 Loading schema from INFORMATION_SCHEMA...")
    get_schema()

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in {"exit", "quit"}:
            print("👋 Goodbye!")
            break

        try:
            sql, df, explanation = agent_query(user_input)
            print("\n✅ Generated SQL:\n", sql)
            print("\n📄 Results Preview:")
            print(df.head())
            print("\n📝 AI Explanation:\n", explanation)
        except Exception as e:
            print("❌ Query failed:", e)
