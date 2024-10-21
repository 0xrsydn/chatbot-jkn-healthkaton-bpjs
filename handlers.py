from groq_client import call_groq_llm

def handle_greeting():
    return "Halo Sahabat Sehat! Terima kasih telah menghubungi layanan chatbot BPJS Kesehatan. Ada yang bisa saya bantu?"

def handle_farewell():
    return "Selamat tinggal Sahabat Sehat! Semoga informasi yang saya berikan bermanfaat. Jangan ragu untuk menghubungi saya lagi jika ada pertanyaan lain."

def handle_nocontext():
    return "Mohon maaf Sahabat Sehat! Saat ini kami tidak memiliki informasi terkait pertanyaan anda. Untuk bertanya lebih detail bisa contact ke 911."

def handle_location():
    return "Locations Hospital"

def handle_faq(query, retriever):
    # Retrieve context from FAQ and call Groq to generate response
    context = retriever.get_relevant_documents(query)
    faq_prompt_template = """Answer the question based only on the following context:
    {context}

    Question: {question}
    Answer:"""
    faq_prompt = faq_prompt_template.format(context=context, question=query)
    return call_groq_llm(faq_prompt)

def handle_intent(intent, query, retriever):
    if intent == 'greeting':
        return handle_greeting()
    elif intent == 'farewell':
        return handle_farewell()
    elif intent == 'location':
        return handle_location()
    elif intent == 'question':
        return handle_faq(query, retriever)
    elif intent == 'no context':
        return handle_nocontext()
    else:
        return "Mohon maaf Sahabat Sehat! Saat ini kami tidak memiliki informasi terkait pertanyaan anda. Untuk bertanya lebih detail bisa contact ke 911."
