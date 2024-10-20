# pull official base image
FROM python:3.10.14-slim

# set work directory
WORKDIR /usr/src/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

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