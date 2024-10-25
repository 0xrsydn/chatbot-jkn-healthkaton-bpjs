# Start with a base image containing Python
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/

# Copy the requirements file and install dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# # Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Run the Flask app
CMD ["python", "main.py"]
