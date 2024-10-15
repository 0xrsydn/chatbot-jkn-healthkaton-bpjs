import gradio as gr
import json
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough

# Load the FAQ JSON data
with open('/Users/rasyidanakbar/Documents/bpjs_faq.json', 'r', encoding='utf-8') as f:
    faq_data = json.load(f)

# Prepare questions and answers into a single text block for each FAQ
faq_texts = [f"Question: {faq['question']}\nAnswer: {faq['answer']}" for faq in faq_data]

# Initialize FastEmbed embeddings
embeddings = FastEmbedEmbeddings()

# Create the FAISS index for similarity search
vectorstore = FAISS.from_texts(faq_texts, embeddings)

# Initialize the Ollama chat model
llm = ChatOllama(model="llama3.2:3b")

# Create the retriever
retriever = vectorstore.as_retriever()

# Create the prompt template
template = """Answer the question based only on the following context:
{context}

Question: {question}
Answer:"""
prompt = ChatPromptTemplate.from_template(template)

# Create the RAG chain
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Function to generate chatbot response
def chatbot(query, history):
    response = chain.invoke(query)
    history.append((query, response))
    return history, ""

# Create the Gradio interface
with gr.Blocks() as demo:
    chatbot_ui = gr.Chatbot(label="BPJS FAQ Chatbot")
    with gr.Row():
        user_input = gr.Textbox(label="Enter your question here")
        send_button = gr.Button("Send")
    
    send_button.click(chatbot, [user_input, chatbot_ui], [chatbot_ui, user_input])

# Launch the Gradio app
if __name__ == "__main__":
    demo.launch()
