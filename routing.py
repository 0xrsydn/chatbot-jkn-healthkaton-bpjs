from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from groq_client import call_groq_llm

# Routing prompt for classifying user query
routing_prompt = """Given the user question below, classify the user's intention.

Do not respond with more than one word.

Greeting: If the user greets you.
Question: If the user asks a general question about the company.
Summary: If the user specifically asks you to create a summary of the chat.
Farewell: If the user says goodbye or farewell.
Location: If the user asks about hospital locations.
Room: If the user asks about hospital room availability.
Chit-chat: If the user input a chit-chat.
No Context: If the user’s question is unrelated to any of the categories above or lacks enough context to classify.

<question>
{question}
</question>

Classification:"""

ROUTING_PROMPT = PromptTemplate(template=routing_prompt, input_variables=["question"])

def classify_query(query):
    routing_chain = {"question": RunnablePassthrough()} | ROUTING_PROMPT
    routing_prompt = routing_chain.invoke(query)

    # Extract text properly from StringPromptValue
    if hasattr(routing_prompt, "text"):
        routing_prompt = routing_prompt.text

    # Call Groq LLM for routing
    classification = call_groq_llm(routing_prompt)
    return classification.strip().lower()
