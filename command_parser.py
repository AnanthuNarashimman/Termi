import json
import subprocess
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

def agent():

    # initializing sandbox directory
    workspace = os.path.join(os.getcwd(), "workspace")
    os.makedirs(workspace, exist_ok=True)
    print(f"Agent sandbox initialized at :{workspace}\n")

    while True:
        user_prompt = input("Enter Purpose (or 'exit'):")

        if user_prompt.lower() == "exit":
            return None
        

        # API calling
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt,
            config = types.GenerateContentConfig(
                system_instruction="""You are an expert Ubuntu filesystem assistant. 
                Your only capability is to translate user intents into precise Ubuntu terminal commands.
                Output strictly in JSON format: {"action": "description", "command": "bash command"}"""
            )
        )

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

        choice = input("\nExecute (y/n)?")
        if(choice.lower() == 'y'):
            print("Executing...")

            result = subprocess.run(
                bash_command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=workspace
            )

            print(f"\n ----STDOUT---- \n {result.stdout.strip()}")

            if result.stderr:
                print(f"\n ----STDERR---- \n {result.stderr.strip()}")

        else:
            print("Execution Aborted")



if __name__ == "__main__":
    agent()