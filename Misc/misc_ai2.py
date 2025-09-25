import getpass
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

if "AI_API_KEY" not in os.environ:
    os.environ["AI_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")

# Instantiate LLM model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

# Invoke langchain
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that translates {input_language} to {output_language}.",
        ),
        ("human", "{input}"),
    ]
)

chain = prompt | llm

ai_msg = chain.invoke(
    {
        "input_language": "English",
        "output_language": "Spanish",
        "input": "How are you today?",
    }
)



# messages = [
#     (
#         "system",
#         "You are a helpful assistant that translates English to French. Translate the user sentence.",
#     ),
#     ("human", "I love programming."),
# ]
# ai_msg = llm.invoke(messages)
print(ai_msg.content)

