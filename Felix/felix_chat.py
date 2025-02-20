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

def run_command(command):
    """Runs a system command securely and returns the output."""
    try:
        # Confirm before running any command
        confirm = input(f"\033[93mAre you sure you want to run: {command}? (yes/no): \033[0m").strip().lower()
        if confirm != "yes":
            return "\033[91mCommand execution cancelled.\033[0m"

        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return f"\033[96m[Command Output]\033[0m\n{result.stdout}" if result.stdout else "\033[91mNo output or command failed.\033[0m"
    except Exception as e:
        return f"\033[91mError executing command: {str(e)}\033[0m"

def process_file_command(user_input):
    """Parses natural language file commands and translates them into system commands."""
    
    # Predefined paths (can be expanded)
    paths = {
        "downloads": "~/Downloads",
        "minecraft plugins": "~/Projects/Minecraft_Server/plugins",
        "minecraft server": "~/Minecraft_Server"
    }
    
    # Match file operations
    move_match = re.search(r"move (.+) from (.+) to (.+)", user_input, re.IGNORECASE)
    copy_match = re.search(r"copy (.+) from (.+) to (.+)", user_input, re.IGNORECASE)
    delete_match = re.search(r"delete (.+) from (.+)", user_input, re.IGNORECASE)

    if move_match:
        file, source, destination = move_match.groups()
        src_path = paths.get(source.lower(), source)
        dest_path = paths.get(destination.lower(), destination)
        command = f"mv {src_path}/{file} {dest_path}/"
    
    elif copy_match:
        file, source, destination = copy_match.groups()
        src_path = paths.get(source.lower(), source)
        dest_path = paths.get(destination.lower(), destination)
        command = f"cp {src_path}/{file} {dest_path}/"

    elif delete_match:
        file, source = delete_match.groups()
        src_path = paths.get(source.lower(), source)
        command = f"rm {src_path}/{file}"
    
    else:
        return "\033[91mI couldn't understand the file command.\033[0m"

    # Confirm execution
    confirm = input(f"\033[93mAre you sure you want to run: {command}? (yes/no): \033[0m").strip().lower()
    if confirm != "yes":
        return "\033[91mCommand execution cancelled.\033[0m"
    
    return run_command(command)

if __name__ == "__main__":
    print("\033[94mFelix: Hi, I'm Felix! How can I help? (Type 'exit' to quit)\033[0m")
    while True:
        if any(word in user_input.lower() for word in ["move", "copy", "delete"]):
            response = process_file_command(user_input)
        elif user_input.startswith("run "):  # User wants to execute a manual command
            command = user_input[4:].strip()
            response = run_command(command)
        else:
            response = chat_with_gemini(user_input)


