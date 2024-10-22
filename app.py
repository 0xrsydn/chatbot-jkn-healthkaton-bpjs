import gradio as gr
import requests
import time
from routing import classify_query
from handlers import handle_intent
from faq import load_faq_data, initialize_retriever

# Flask API URL for Rasa /chat/ Endpoint
FLASK_API_URL = "http://localhost:5000/chat/"

# Initialize FAQ Data and Retriever
faq_data, faq_texts = load_faq_data('data/bpjs_faq.json')
retriever = initialize_retriever(faq_texts)

def chatbot(query, history):
    intent = classify_query(query)
    if intent == "location":
        try:
            # Check the user query to the FLASK API (which calls Rasa)
            response = requests.post(FLASK_API_URL, json={"message": query})

            # Check if the response is successful
            if response.status_code == 200:
                bot_responses = response.json() # List of bot responses
            else:
                bot_responses = [{"text" : "Maaf, Bot terdapat kendala. Mohon coba lagi untuk beberapa saat. Terimakasih."}]
        
        except Exception as e:
            bot_responses = [{"text" : "Maaf, Bot terdapat kendala. Mohon coba lagi untuk beberapa saat. Terimakasih."}]

        # Append each bot response one-by-one to the chat history
        for bot_response in bot_responses:
            bot_reply = bot_response.get("text", "")
            history.append((query, bot_reply))
            query = None

            time.sleep(1)
    else:        
        response = handle_intent(intent, query, retriever)
        
        history.append((query, response))
    return history, ""

with gr.Blocks() as demo:
    chatbot_ui = gr.Chatbot(label="BPJS FAQ Chatbot")
    with gr.Row():
        user_input = gr.Textbox(label="Enter your question here")
        send_button = gr.Button("Send")
    
    send_button.click(chatbot, [user_input, chatbot_ui], [chatbot_ui, user_input])

if __name__ == "__main__":
    demo.launch()
