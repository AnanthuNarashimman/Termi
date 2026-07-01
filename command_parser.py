import json
import subprocess
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()


def get_directory_tree(cwd):

    try:
        tree_cmd = "powershell -Command \"Get-ChildItem -Recurse -Depth 3 -Force | Where-Object { $_.Name -notlike '.*' } | Select-Object FullName | Sort-Object FullName\""
        return subprocess.check_output(tree_cmd,
                                       shell=True,
                                       cwd=cwd,
                                       text=True).strip()
    except subprocess.CalledProcessError:
        return "Error reading directory tree."
    

def agent():
    workspace = os.path.join(os.getcwd(), "workspace")
    os.makedirs(workspace, exist_ok=True)
    current_cwd = workspace

    print(f"Agent sandbox initialized at: {workspace}\n")

    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction="""You are an expert Windows PowerShell filesystem assistant. 
            You receive the current working directory and directory contents before each request.
            Output strictly in JSON format: {"action": "description", "command": "powershell command"}"""
        )
    )

    success = False

    while True:

        user_prompt = input("\nEnter Purpose (or 'exit'): ")
        
        if not user_prompt.strip():
            continue
            
        if user_prompt.lower() == "exit":
            break

        MAX_RETRIES = 3
        attempt = 0
        success = False
        last_stderr = ""

        while attempt < MAX_RETRIES and not success:

            current_files = get_directory_tree(current_cwd)

            if attempt == 0:
                context_prompt = f"CURRENT STATE:\nWorking Directory: {current_cwd}\nFiles:\n{current_files}\n\nUSER REQUEST: {user_prompt}"
            else:
                print(f"\n[Agent internal reasoning: Attempting error recovery {attempt}/{MAX_RETRIES}]")
                context_prompt = f"CURRENT STATE:\nWorking Directory: {current_cwd}\nFiles:\n{current_files}\n\nPREVIOUS ERROR:\nThe last command failed with: {last_stderr}\nFix the command to achieve the user request: {user_prompt}"

            response = chat.send_message(context_prompt)
            raw_text = response.text

            try:
                clean_text = raw_text.strip(" `\n").removeprefix("json\n")
                parsed_json = json.loads(clean_text)
                action_desc = parsed_json.get("action")
                bash_command = parsed_json.get("command")
            except json.JSONDecodeError:
                print(f"Error: Model failed to output a valid JSON. Raw output: \n{raw_text}")
                last_stderr = "You did not output valid JSON. Ensure your output is strictly a JSON object."
                attempt += 1
                continue

            print(f"\nAction: {action_desc}")
            print(f"Command: {bash_command}")

            choice = input("Execute (y/n)? ")
            if choice.lower() != 'y':
                print("Execution Aborted by user.")
                break

            print("Executing...")

            result = subprocess.run(
                ["powershell", "-Command", bash_command],
                capture_output=True,
                text=True,
                cwd=current_cwd
            )

            if result.returncode == 0:
                if bash_command.startswith("cd ") or bash_command.startswith("Set-Location "):
                    parts = bash_command.split(" ", 1)
                    if len(parts) > 1:
                        target_dir = parts[1].split(";")[0].strip("\"' ")
                        potential_new_cwd = os.path.abspath(os.path.join(current_cwd, target_dir))

                        if os.path.exists(potential_new_cwd) and workspace in potential_new_cwd:
                            current_cwd = potential_new_cwd
                            print(f"[State Updated] Changed directory to: {current_cwd}")
                        else:
                            print("[Security Block] Directory does not exist or escapes sandbox.")

                print(result.stdout)
                print("Operation completed successfully.")
                success = True 
                break 

            else:
                print(f"\n----STDERR----\n{result.stderr.strip()}")
                last_stderr = result.stderr.strip()
                attempt += 1

        if not success and choice.lower() == 'y':
            print(f"Agent failed to complete the task after {MAX_RETRIES} attempts. Task aborted.")


if __name__ == "__main__":
    agent()    