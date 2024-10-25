import gradio as gr
from routing import classify_query
from handlers import handle_intent
from faq import load_faq_data, initialize_retriever

# Initialize FAQ Data and Retriever
faq_data, faq_texts = load_faq_data('data/bpjs_faq.json')
retriever = initialize_retriever(faq_texts)

def chatbot(query, history):
    intent = classify_query(query)

    print("intent: ", intent)

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
