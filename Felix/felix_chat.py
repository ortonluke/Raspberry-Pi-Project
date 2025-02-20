import os
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

if __name__ == "__main__":
    print("\033[94mFelix: Hi, I'm Felix! How can I help?\033[0m")
    print("Type 'exit' to quit.")
    while True:
        user_input = input("\033[92mInput: \033[0m")
        if user_input.lower() == "exit":
            print("\033[94mFelix: Goodbye!\033[0m")
            break
        response = chat_with_gemini(user_input)
        print("\033[94mFelix:\033[0m", response)
