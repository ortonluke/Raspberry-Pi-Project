import os
import re
import requests
import json
import subprocess

# Replace with your actual API key
API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + API_KEY

def chat_with_gemini(user_input):
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": user_input}]}]
    }
    
    response = requests.post(API_URL, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        response_data = response.json()
        try:
            return response_data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return "\033[91mError: Unexpected response format.\033[0m"
    else:
        return f"\033[91mError: {response.status_code} - {response.text}\033[0m"

def generate_command(user_request):
    """Asks Gemini AI to generate a terminal command from a user request."""
    prompt = (
        "Convert the following natural language request into a Linux terminal command.\n"
        "Only return the command, no explanations.\n"
        "Request: " + user_request
    )
    
    command = chat_with_gemini(prompt).strip()
    
    # Ensure AI didn’t return anything weird (like explanations)
    if "\n" in command or "```" in command.lower():
        return "\033[91mError: AI response was not a valid single command.\033[0m"
    
    return command

def run_command(command):
    """Runs a command securely after user confirmation."""
    try:
        confirm = input(f"\033[93mAre you sure you want to run: {command}? (yes/no): \033[0m").strip().lower()
        if confirm != "yes":
            return "\033[91mCommand execution cancelled.\033[0m"

        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return f"\033[96mDone!\033[0m\n{result.stdout}" #if result.stdout else "\033[91mNo output or command failed.\033[0m"
    except Exception as e:
        return f"\033[91mError executing command: {str(e)}\033[0m"

if __name__ == "__main__":
    print("\033[94mFelix: Hi, I'm Felix! How can I help? (Type 'exit' to quit)\033[0m")
    print()
    while True:
        user_input = input("\033[92mInput: \033[0m")
        
        if user_input.lower() == "exit":
            print("\033[94mFelix: Goodbye!\033[0m")
            break
        
        if user_input.startswith("@command"):
            command_request = user_input[len("@command"):].strip()
            command = generate_command(command_request)
            if "Error" in command:
                response = "FAILED" + command  # Show error if AI failed
            else:
                response = run_command(command)
        else:
            response = chat_with_gemini(user_input)

        print("\033[94mFelix:\033[0m", response)


