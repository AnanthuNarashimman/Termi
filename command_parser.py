import json
import subprocess
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

def agent():

    workspace = os.path.join(os.getcwd(), "workspace")
    os.makedirs(workspace, exist_ok=True)
    current_cwd = workspace

    print(f"Agent sandbox initialized at: {workspace}\n")

    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction="""You are an expert Ubuntu filesystem assistant. 
            You receive the current working directory and directory contents before each request.
            Output strictly in JSON format: {"action": "description", "command": "bash command"}"""
        )
    )

    while True:
        user_prompt = input("Enter Purpose (or 'exit'):")
        if user_prompt.lower() == "exit": 
            break

        try:
            current_files = subprocess.check_output("ls -l", shell=True, cwd=current_cwd, text=True).strip()
        except subprocess.CalledProcessError:
            current_files = "Error reading directory."

        context_prompt = f"""
        CURRENT STATE:
        Working Directory: {current_cwd}
        Files in Directory: 
        {current_files}
        
        USER REQUEST: {user_prompt}
        """

        response = chat.send_message(context_prompt)
        raw_text = response.text

        try:
            clean_text = raw_text.strip(" `\n").removeprefix("json\n")
            parsed_json = json.loads(clean_text)
            action_desc = parsed_json.get("action")
            bash_command = parsed_json.get("command")
        except json.JSONDecodeError:
            print(f"Error: Model failed to output a valid JSON. Raw output: \n{raw_text}")
            continue

        print(f"\nAction: {action_desc}")
        print(f"Command: {bash_command}")

        choice = input("Execute (y/n)?")

        if(choice.lower() == 'y'):
            print("Executing...")

            result = subprocess.run(
                bash_command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=current_cwd
            )

            if bash_command.startswith("cd"):
                target_dir = bash_command.split("cd ")[1].split("&&")[0].strip()
                potential_new_cwd = os.path.abspath(os.path.join(current_cwd, target_dir))

                if os.path.exists(potential_new_cwd) and workspace in potential_new_cwd:
                    current_cwd = potential_new_cwd
                    print(f"[State Updated] Changed directory to: {current_cwd}")

                else:
                    print("[Security Block] Directory does not exist or escapes sandbox.")

            print(result.stdout)

            if result.stderr:
                print(f"\n----STDERR----\n{result.stderr.strip()}")
        else:
            print("Execution Aborted")


if __name__ == "__main__":
    agent()


