import os
import re
import requests
import json
import subprocess

# Replace with your actual API key
API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + API_KEY

#Folder Memory System
FOLDER_ALIAS_FILE = "folder_aliases.json"

def load_folder_aliases():
    if os.path.exists(FOLDER_ALIAS_FILE):
        with open(FOLDER_ALIAS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_folder_aliases(aliases):
    with open(FOLDER_ALIAS_FILE, "w") as f:
        json.dump(aliases, f, indent=4)

FOLDER_ALIASES = load_folder_aliases()

def resolve_folder_alias(text):
    for alias in FOLDER_ALIASES:
        if alias in text.lower():
            return text.lower().replace(alias, FOLDER_ALIASES[alias])
    return None  # Return None if no match

def prompt_for_folder(alias_name):
    print(f"\033[93mFelix: I don't know where your '{alias_name}' is. Where can I find it?\033[0m")
    user_path = input("Path: ").strip()
    full_path = os.path.expanduser(user_path)

    if os.path.isdir(full_path):
        FOLDER_ALIASES[alias_name] = full_path
        save_folder_aliases(FOLDER_ALIASES)
        print("\033[92mGot it! I'll remember that.\033[0m")
        return full_path
    else:
        print("\033[91mThat path doesn't exist. Skipping.\033[0m")
        return None

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
            
            # Try resolving any known aliases
            for alias in FOLDER_ALIASES:
                if alias in command_request.lower():
                    command_request = command_request.lower().replace(alias, FOLDER_ALIASES[alias])
                
            # Check for unknown folder references
            folder_pattern = re.findall(r"(my [\w\s\-]+ folder)", command_request.lower())
            for alias in folder_pattern:
                if alias not in FOLDER_ALIASES:
                    resolved = prompt_for_folder(alias)
                    if resolved:
                        command_request = command_request.lower().replace(alias, resolved)
                
            command = generate_command(command_request)
            if "Error" in command:
                response = "FAILED" + command  # Show error if AI failed
            else:
                response = run_command(command)
        else:
            response = chat_with_gemini(user_input)

        print("\033[94mFelix:\033[0m", response)


