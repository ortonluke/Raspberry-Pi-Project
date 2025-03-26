import subprocess
import os

# Ensure the environment variables are passed to the new terminal
env = os.environ.copy()

subprocess.Popen(["lxterminal", "-e", "bash", "-c", "python3 /home/pumpkin-pi/Projects/Felix/felix_chat.py"], env=env)
