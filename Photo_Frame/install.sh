#!/bin/bash

echo "Updating system..."
sudo apt update && sudo apt upgrade -y

echo "Installing Python and dependencies..."
sudo apt install -y python3 python3-pip
pip3 install --upgrade pip
pip3 install pygame pillow google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

echo "Checking for credentials.json..."
if [ ! -f "credentials.json" ]; then
    echo "⚠️  Missing credentials.json! Please add it to the project folder."
    exit 1
fi

echo "Setup complete! You can now run the program using:"
echo "python3 main.py"
