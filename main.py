from mcp.server.fastmcp import FastMCP
import os

mcp =FastMCP("AI Notes")
NOTES_FILE = os.path.join(os.path.dirname(__file__), "notes.txt")


def ensure_file():
    if not os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "w") as f:
            f.write("")

@mcp.tool()

def add_note(message : str) -> str:
    """
    this python function helps us to 
    append a new note to NOTES_FILE file
    """
    ensure_file()
    with open(NOTES_FILE , "a") as f:
        f.write(message + "\n" )
    return "notes saved"

@mcp.tool()

def read_notes() -> str:

    """
    this python function helps us to 
    READ a new note to NOTES_FILE file
    """
    ensure_file()
    with open(NOTES_FILE , "r") as f:
        content = f.read().strip()
    return content or "no content yet"
    
@mcp.resource("notes://latest")

def latest_note() -> str :

    """
    this python function helps us to 
    TAKE OUT THE LATEST NODE FROM THE NOTES a new note to NOTES_FILE file
    """
    ensure_file()
    with open(NOTES_FILE, "r") as f:
        lines = f.readlines()
    return lines[-1].strip() if lines else "no otes yet"

@mcp.prompt()

def notes_summary_prompt() -> str:

    """
    this python function helps us to 
    READ a new note to NOTES_FILE file

    """
    ensure_file()
    with open(NOTES_FILE,  "r") as f:
        content = f.read().strip()

    if not content:
        return "there is no content yet"
    return f"Summarize the current note {content }"

# if __name__ == "__main__":
#     mcp.run()
