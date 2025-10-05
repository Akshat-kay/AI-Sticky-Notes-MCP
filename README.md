# AI Sticky Notes MCP 🗒️🤖

*A tiny, teach-by-doing MCP server you can copy, run, and extend—in minutes.*

This repo shows how to build a **Model Context Protocol (MCP)** server that lets an AI app (like **Claude Desktop**) **write and read notes on your computer**. It’s intentionally small so anyone can understand the moving parts and adapt it for **their own automations**.

---

## Why MCP?

LLMs are great at language, but they can’t touch your files or tools by themselves. **MCP** is the standard way to safely give an AI **tools** (read a file, call an API, query a DB). This project exposes four simple tools:

* `add_note(message)` — append a line to a local `notes.txt`
* `read_notes()` — read all notes
* `notes_summary()` — return a short LLM-friendly summary
* `notes://latest` — a resource that returns the **last** note

Use this as a **pattern** to automate anything: to-do lists, file workflows, scripts, APIs, etc.

---

## Quick start (5–10 minutes)

### 1) Requirements

* **Python 3.10+**
* **uv** (recommended) → `pipx install uv` or download from Astral
* Claude Desktop (or any MCP client)

### 2) Clone & install

```bash
git clone https://github.com/Akshat-kay/AI-Sticky-Notes-MCP.git
cd AI-Sticky-Notes-MCP
uv sync      # installs deps using pyproject.toml / uv.lock
```

> No uv? Use pip:
>
> ```bash
> python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
> pip install -r <(uv pip compile pyproject.toml)     # or just: pip install fastmcp
> ```

### 3) Run the server

```bash
python main.py
```

It starts an MCP server over **stdio** (no open ports, no cloud). Your MCP client will spawn this process when needed.

### 4) Hook it into Claude Desktop

1. Open **Claude Desktop → Settings → Tools (MCP)**
2. **Add local server**

   * **Command:** `python`
   * **Args:** `main.py`
   * **Working directory:** the repo folder
3. Save, then toggle the server on.

You’ll see tools: **add_note**, **read_notes**, and the resource **notes://latest**.

---

## Try these prompts

* **Add LLM facts**

  ```
  add 10 random facts about how LLMs work to notes
  ```

* **Prepare for an MCP interview (automation focus)**

  ```
  Add 8 scenario-based MCP interview prep notes focused on automation development.
  ```

* **Summarize**

  ```
  Give me a short summary of the LLM notes and the MCP interview notes separately,
  then add a few lines on how they are related.
  ```

* **Fetch last note (resource)**

  ```
  Fetch resource: notes://latest
  ```

---

## How it works (plain English)

* **FastMCP server**: a tiny Python app that registers **tools** and **resources**.
* **Tools** are functions the AI can call with parameters.
* **Resources** are read-only URIs the AI can fetch (like `notes://latest`).
* **Claude/MCP client** auto-discovers tools and asks for permission before running them.

---

## Code you can reuse

Below is a **minimal pattern** for any file-based tool. Copy it into a new tool and change the body.

```python
from mcp.server.fastmcp import FastMCP
import os

mcp = FastMCP("Sticky Notes")
BASE = os.path.dirname(__file__)
NOTES_PATH = os.path.join(BASE, "notes.txt")

def ensure_file():
    os.makedirs(BASE, exist_ok=True)
    if not os.path.exists(NOTES_PATH):
        with open(NOTES_PATH, "w", encoding="utf-8") as f:
            f.write("")

@mcp.tool()
def add_note(message: str) -> str:
    """Append a note (one line) to notes.txt."""
    ensure_file()
    with open(NOTES_PATH, "a", encoding="utf-8") as f:
        f.write(message.rstrip() + "\n")
    return "note saved"

@mcp.tool()
def read_notes() -> str:
    """Return the full notes file."""
    ensure_file()
    with open(NOTES_PATH, "r", encoding="utf-8") as f:
        content = f.read().strip()
    return content or "no notes yet"

@mcp.tool()
def notes_summary() -> str:
    """Return a lightweight natural-language summary (LLM-friendly)."""
    ensure_file()
    with open(NOTES_PATH, "r", encoding="utf-8") as f:
        content = f.read().strip()
    return "there are no notes yet" if not content else f"Summary:\n{content[:2000]}"

@mcp.resource("notes://latest")
def latest_note():
    """Return the last line as a resource (bytes, mime)."""
    ensure_file()
    with open(NOTES_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    latest = lines[-1].strip() if lines else "no notes yet"
    return latest.encode("utf-8"), "text/plain"

if __name__ == "__main__":
    mcp.run()
```

---

## Customize for your own automations

* **Call a shell command**

  ```python
  @mcp.tool()
  def run_script(name: str) -> str:
      # validate 'name' against an allow-list to avoid injection
      ...
  ```

* **Talk to an API**

  ```python
  @mcp.tool()
  def get_weather(city: str) -> dict:
      # use requests/httpx; return small JSON the LLM can reason about
      ...
  ```

* **Query a database**

  ```python
  @mcp.tool()
  def list_tasks(status: str = "open") -> list[dict]:
      # use parameterized queries; never string-format SQL
      ...
  ```

**Design tips**

* Keep **inputs small and explicit** (the model reasons better).
* Return **compact JSON or plain text** (saves tokens; easier to parse).
* Add **docstrings**—LLMs read them to learn how to use your tool.

---

## Security & safety (copy this mindset)

* **No secrets in code**. Load from environment variables; commit a `*.env.example`.
* **Least privilege**: limit file paths; refuse `..` or absolute paths.
* **Input validation**: length limits, allow-lists for commands, sanitize filenames.
* **Lock dependencies**: commit `uv.lock`, enable Dependabot & CI audits.
* **Separate data from code**: don’t commit runtime files like `notes.txt`.
* **Run as a non-admin user** when possible.

> Add this to `.gitignore`:

```gitignore
.venv/
__pycache__/
*.pyc
notes.txt
.env
*.log
.vscode/
.idea/
.DS_Store
Thumbs.db
```

---

## Troubleshooting (fast fixes)

* **“response was interrupted” in Claude** → your server likely crashed.

  * Ensure you end with `mcp.run()` (not `main()`), and actually call `ensure_file()`.
  * Run `python main.py` in a terminal to see errors.

* **Claude can’t find the server**

  * Check the **working directory** and **args** in the MCP settings.
  * On Windows, confirm `python` points to the right interpreter (`py -V`, `where python`).

* **Unicode or line endings look odd**

  * Always open files with `encoding="utf-8"` and use `\n`.

---

## Learn more / next steps

* Add tags & titles to notes (JSON lines) and build a **search** tool.
* Create a **scheduler** tool (e.g., run at intervals) with safety prompts.
* Wrap internal systems behind MCP tools to give the AI “hands”—safely.

---

## Contributing

Issues and PRs welcome—keep examples **small, safe, and well-commented** so folks learning MCP can follow along.

## License

MIT (feel free to reuse in your own projects).
