# pull official base image
FROM python:3.10.14-slim

# set work directory
WORKDIR /usr/src/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV GROQ_API_KEY=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 \
    RASA_PRO_LICENSE=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIxNjM5MjdiZS0zMzA3LTQ3MGUtODliMy05OTVjNTM0NDY4YzAiLCJpYXQiOjE3MjM2OTQxNzksIm5iZiI6MTcyMzY5NDE3Nywic2NvcGUiOiJyYXNhOnBybyByYXNhOnBybzpjaGFtcGlvbiIsImV4cCI6MTgxODMwMjE3NywiZW1haWwiOiJmaXJxYUBhaWNoYXQuY29tIiwiY29tcGFueSI6IlJhc2EgQ2hhbXBpb25zIn0.nrkBTXUIv1cXIbUd8ZCO669NvsJElCTTr5N3dD1Z9XZU-HNg0rnVw8CPzwXrWBJFJYu32pWVUgnEc12j0dVusE3vW9vkTijFJwgdbFAT8BS7G8udoRQ4BdUppGU4mNUZzNqEk3LhH2EJJlELUMNyiwd54WFM0vZdvLqTgfi1kSAcg9o-Jc6FNK05wyUaFb4abwmN0H50ckeXHWYPeWZ-jLCWxrrWEiu5V_ahsJ6hRurfyfQakLC6n5CoyxTJfGqdjP_GbN18FBoJW3Z8ng7Wyr-1-2cs1yDnGHQyblQ_fv7TIeAV1nko7WaEnbJ0YlTOh0pT1MqqN7CdyXp8ig1ogA

# install dependencies
RUN apt-get update --fix-missing
RUN apt-get install build-essential -y

RUN pip install --upgrade pip
RUN pip install uv
RUN uv pip install rasa-pro --system --extra-index-url=https://europe-west3-python.pkg.dev/rasa-releases/rasa-pro-python/simple/ 
COPY ./requirements.txt /usr/src/requirements.txt
RUN pip install -r requirements.txt

# Expose the necessary ports
EXPOSE 5005 
EXPOSE 5055
EXPOSE 5000

# Command to run Rasa and the action server
CMD ["bash", "-c", "rasa run --enable-api & rasa run actions & python main.py"]