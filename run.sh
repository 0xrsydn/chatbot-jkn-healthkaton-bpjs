#!/bin/bash

# Define paths to your service directories and the Gradio app
SERVICE_DIR1="./hospital"  # Replace with the path to your first service folder
SERVICE_DIR2="./langdetect"  # Replace with the path to your second service folder
SERVICE_DIR3="./translation"
MAIN_APP="app.py"          # Path to your Gradio app

# Start the first service with Docker Compose
echo "Starting Rasa Service ..."
(cd "$SERVICE_DIR1" && docker compose up -d)
if [ $? -ne 0 ]; then
    echo "Failed to start service 1"
    exit 1
fi

# Start the second service with Docker Compose
echo "Starting Language Detection Service ..."
(cd "$SERVICE_DIR2" && docker compose up -d)
if [ $? -ne 0 ]; then
    echo "Failed to start service 2"
    exit 1
fi


# Start the second service with Docker Compose
echo "Starting Language Translation Service ..."
(cd "$SERVICE_DIR3" && docker compose up -d)
if [ $? -ne 0 ]; then
    echo "Failed to start service 3"
    exit 1
fi

# Run the Gradio main app
echo "Starting Gradio app..."
gradio "$MAIN_APP"
if [ $? -ne 0 ]; then
    echo "Failed to start Gradio app"
    exit 1
fi

# Optional: Clean up Docker services after Gradio app exits
echo "Stopping services..."
(cd "$SERVICE_DIR1" && docker compose down)
(cd "$SERVICE_DIR2" && docker compose down)

echo "All services stopped."
