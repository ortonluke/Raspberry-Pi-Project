#!/bin/bash

echo "Updating system..."
sudo apt update && sudo apt upgrade -y

echo "Installing Python and dependencies..."
sudo apt install -y python3 python3-pip python3-venv

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install pygame pillow google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

echo "Checking for credentials.json..."
if [ ! -f "credentials.json" ]; then
    echo "⚠️  Missing credentials.json! Please add it to the project folder."
    exit 1
fi

echo "Setup complete! You can now run the program using:"
echo "python3 main.py"
