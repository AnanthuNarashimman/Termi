
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client()

def agent():

    while(True):
        prompt = input("Enter purpose:")

        if(prompt == "exit"):
            return None

        interaction = client.interactions.create(
        model="gemini-2.5-flash-lite",
        input= prompt,
        system_instruction="""You are an expert Ubuntu filesystem assistant. Your purpose is to translate user intents into precise Ubuntu terminal commands for file navigation and management.
                        OPERATING CONTEXT:
                        Assume a standard Ubuntu environment. Treat all files, directories, and paths mentioned by the user as if they already exist. Do not ask for verification.

                        OUTPUT FORMAT:
                        You must respond strictly with a valid JSON object. Do not include introductory text, explanations, or markdown formatting (do not use ```json block ticks). 

                        Use this exact JSON schema:
                        {
                        "action": "A brief, 1-2 sentence description of what the command will do",
                        "command": "The exact bash command to execute"
                        }
                        """
                        )   
        print(interaction.output_text)

        choice = input("Execute(y/n)?")
        if(choice.lower == 'y'):
            print("Done!")
        else:
            print("My bad!")


if __name__ == "__main__":
    agent()