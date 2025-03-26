import subprocess
import os

# Ensure the environment variables are passed to the new terminal
env = os.environ.copy()

# Modify the command to keep the terminal open even after execution
command = "python3 /home/pumpkin-pi/Projects/Felix/felix_chat.py; read -p 'Press Enter to close...'"
subprocess.Popen(["lxterminal", "-e", "bash", "-c", command], env=env)
