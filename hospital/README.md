# **JKN Rasa Endpoint**

The **JKN (Jaminan Kesehatan Nasional)** chat endpoint is built with **Rasa CALM** (Conversational AI with Language Model). It leverages a **Large Language Model (LLM)** along with conversational flows to create a robust **Conversational Experience (CX)** for the JKN chatbot.

## **How to Use**

### Build and Run the Docker Containers:

To build and run the project using Docker, execute the following commands:

```bash
docker-compose build
docker-compose up
```

## **Chat Endpoint:**
The chatbot can be accessed at the following endpoint:

```bash
http://localhost:5000/chat/
```

## **Example Payload:**
To interact with the chatbot, send a POST request to the /chat/ endpoint with the following JSON payload:

```bash
{
    "message": "Saya ingin memesan kamar di rumah sakit Siloam Hospitals Balikpapan"
}
```

## **Example Response:**
The chatbot will respond with a JSON array containing messages like this:
```bash
[
    {
        "recipient_id": "user",
        "text": "Informasi ketersediaan kamar di Siloam Hospitals Balikpapan:\n- Tipe kamar Suite masih tersedia sebanyak 2 kamar.\n- Tipe kamar Kelas 2 masih tersedia sebanyak 10 kamar."
    },
    {
        "recipient_id": "user",
        "text": "Is there anything else you need assistance with?"
    }
]
```