import json
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FastEmbedEmbeddings

def load_faq_data(file_path):
    # Load the FAQ JSON data
    with open(file_path, 'r', encoding='utf-8') as f:
        faq_data = json.load(f)

    # Prepare questions and answers into a single text block for each FAQ
    faq_texts = [f"Question: {faq['question']}\nAnswer: {faq['answer']}" for faq in faq_data]
    return faq_data, faq_texts

def initialize_retriever(faq_texts):
    # Initialize FastEmbed embeddings
    embeddings = FastEmbedEmbeddings()

    # Create the FAISS index for similarity search
    vectorstore = FAISS.from_texts(faq_texts, embeddings)

    # Create the retriever
    return vectorstore.as_retriever()
