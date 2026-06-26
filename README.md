# Termi — AI Terminal Agent

A conversational CLI agent that translates natural language into bash commands using Google Gemini, then executes them inside a sandboxed workspace directory.

## What it does

You describe what you want to accomplish (e.g. "create a folder called projects and add a file called notes.txt"), and the agent:

1. Sends your request along with the current working directory and file tree to Gemini 2.5 Flash.
2. Displays the proposed bash command and a plain-English description of the action.
3. Asks for your confirmation before running anything.
4. Executes the command inside an isolated `workspace/` subdirectory, preventing any writes outside of it.

## Requirements

- Python 3.10+
- A Google Gemini API key

## Setup

```bash
# 1. Clone / enter the project directory
cd agent_workspace

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install google-genai python-dotenv

# 4. Add your Gemini API key
echo "GEMINI_API_KEY=your_key_here" > .env
```

## Running

```bash
python command_parser.py
```

Type a plain-English request at the prompt, review the generated command, and press `y` to run it or `n` to skip. Type `exit` to quit.
