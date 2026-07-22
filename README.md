# AskYourDocs

A **RAG** (Retrieval-Augmented Generation) document Q&A system built
with LangGraph, FastAPI, and DeepSeek LLM.  Users upload documents,
ask questions in natural language, and receive answers grounded in
their own content.

---

## Project Structure

```
D:.
├── skills/                  # Pluggable skill modules (BaseSkill pattern)
│   ├── base.py              # Abstract BaseSkill with Pydantic validation
│   ├── retrieve_knowledge.py# ChromaDB vector retrieval
│   ├── generate_answer.py   # LLM answer generation via DeepSeek
│   ├── add_document.py      # Document chunking + indexing
│   ├── time_skill.py        # Current-time utility skill
│   └── ask_human.py         # Simulated human-in-the-loop approval
│
├── core/                    # Agent orchestration & infrastructure
│   ├── agent.py             # LangGraph StateGraph agent with Skill dispatch
│   ├── callbacks.py         # LangChain callback handler (tool event logging)
│   ├── guardrails.py        # Input injection detection & output redaction
│   └── prompt_loader.py     # YAML-based prompt version manager
│
├── prompts/                 # Prompt templates (YAML, multi-version)
│   └── generate_answer.yaml # System/human prompt versions (v1, v2)
│
├── evaluation/              # Automated evaluation pipeline
│   ├── eval.py              # Agent eval harness with DeepSeek judge
│   └── test_cases.json      # Seed test cases
│
├── tests/                   # Pytest unit tests
│   ├── test_retrieve_knowledge.py
│   ├── test_generate_answer.py
│   ├── test_add_document.py
│   └── test_time_skill.py
│
├── logs/                    # Runtime tool-event logs (JSONL)
│
├── ask_your_docs/
│   └── backend/
│       └── app/             # FastAPI application (register, upload, chat)
│
└── .gitignore
```

---

## Architecture

### Skill System

Every capability is wrapped as a **Skill** — a self-contained class that
extends `BaseSkill[T]`:

| Skill | Input | Output |
|---|---|---|
| `RetrieveKnowledgeSkill` | `query, user_id` | Context string from ChromaDB |
| `GenerateAnswerSkill` | `context, question` | LLM-generated answer |
| `AddDocumentSkill` | `content, user_id, filename` | Number of indexed chunks |
| `TimeSkill` | *(none)* | Current time string |
| `AskHumanSkill` | `reason` | `{"approved": True/False}` after 30s |

**BaseSkill** provides:
* Pydantic input validation via `args_schema`
* Automatic exception logging in the public `run()` method
* Type-safe generic interface (`BaseSkill[T]`)

### Agent

The `Agent` class in `core/agent.py` builds a **LangGraph StateGraph**
that orchestrates Skill instances:

```
user_input → [retrieve] → context → [generate] → answer
                ↑                      │
                └── (while iter < 5) ───┘
```

**Safety boundaries:**
| Guard | Value | Mechanism |
|---|---|---|
| Max iterations | 5 | `_should_continue` conditional edge |
| Timeout | 30 s | `asyncio.wait_for` wrapping the graph |
| Tool whitelist | Registered names | `_validate_tool` before each dispatch |

### Guardrails

`core/guardrails.py` provides two layers of protection:

- **`input_guard(text)`** — Detects prompt injection keywords (Chinese
  & English: `忽略`, `ignore`, `pretend`, `system prompt`, etc.).
  Returns `(cleaned_text, flagged)` tuple.

- **`output_guard(text)`** — Redacts sensitive patterns with
  `[REDACTED]`: IP addresses, SQL fragments, emails, phone numbers.

### Callback Logging

`core/callbacks.py` implements `BaseCallbackHandler` that records every
tool invocation as a JSON line in `logs/agent.log`:
```json
{"event": "tool_start", "tool": "retrieve_knowledge", "input": "..."}
{"event": "tool_end", "tool": "retrieve_knowledge", "duration_ms": 42.0}
{"event": "tool_error", "tool": "generate_answer", "error": "..."}
```

### Prompt Management

`core/prompt_loader.py` loads prompt templates from YAML by version:
```python
from core.prompt_loader import load_prompt
prompt = load_prompt("v1")  # {"system": "...", "human": "..."}
```

### Evaluation

`evaluation/eval.py` runs the Agent against test cases and scores
answer quality with a DeepSeek judge (1–5 scale).  Fails with exit
code 1 if average < 3.5.

---

## Getting Started

### Prerequisites

- Python 3.10+
- A DeepSeek API key (or any OpenAI-compatible endpoint)

### Installation

```bash
cd ask_your_docs/backend
python -m venv .venv
.venv\Scripts\activate    # Windows
# source .venv/bin/activate  # macOS / Linux

pip install -r requirements.txt
```

### Configuration

Create a `.env` file in `ask_your_docs/backend/`:
```env
DEEPSEEK_API_KEY=sk-your-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DATABASE_URL=sqlite:///./ask_your_docs.db
SECRET_KEY=your-secret-key
```

### Run the API Server

```bash
cd ask_your_docs/backend
uvicorn app.main:app --reload --port 8000
```

### Run Tests

```bash
pip install pytest pytest-asyncio
cd D:/project
set PYTHONPATH=D:/project;D:/project/ask_your_docs/backend
pytest tests/ -v
```

---

## License

MIT
