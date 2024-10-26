from groq_client import call_groq_llm

def handle_greeting():
    return "Halo Sahabat Sehat! Terima kasih telah menghubungi layanan chatbot BPJS Kesehatan. Ada yang bisa saya bantu?"

def handle_farewell():
    return "Selamat tinggal Sahabat Sehat! Semoga informasi yang saya berikan bermanfaat. Jangan ragu untuk menghubungi saya lagi jika ada pertanyaan lain."

def handle_nocontext():
    return "Mohon maaf Sahabat Sehat! Saat ini kami tidak memiliki informasi terkait pertanyaan anda. Untuk bertanya lebih detail bisa contact ke 911."

def handle_location():
    return "Locations Hospital"

## Todo: create history chat local storage
def handle_faq(query, retriever, history):
    # Retrieve context from FAQ and call Groq to generate response
    context = retriever.get_relevant_documents(query)
    print(context)
    chat_history_text = "\n".join([f"User: {q}\nBot: {a}" for q, a in history])
    faq_prompt_template = """You are a helpful assistant for BPJS. Here is the previous chat history:
    {chat_history}

    Based on the following FAQ context:
    {context}

    Question: {question}

    Answer:"""
    faq_prompt = faq_prompt_template.format(
        chat_history=chat_history_text,
        context=context,
        question=query
    )
    return call_groq_llm(faq_prompt)

def handle_intent(intent, query, retriever, history):
    if intent == 'greeting':
        return handle_greeting()
    elif intent == 'farewell':
        return handle_farewell()
    elif intent == 'location':
        return handle_location()
    elif intent == 'question':
        return handle_faq(query, retriever, history)
    elif intent == 'no context':
        return handle_nocontext()
    else:
        return "Mohon maaf Sahabat Sehat! Saat ini kami tidak memiliki informasi terkait pertanyaan anda. Untuk bertanya lebih detail bisa contact ke 911."
