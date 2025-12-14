# Universal Agent Starter Kit

A production-ready template for building Agentic AI applications, based on the **Core-Logic Separation** architecture.

## 🌟 Core Philosophy

- **Infrastructure (Core)**: Write once, use everywhere (LLM clients, UI, Parsing).
- **Business Logic (Logic)**: Highly specific to the task (Prompts, Tools).
- **Patterns**: Reusable thought processes (ReAct, Reflection).

## 📂 Structure

```text
template/
├── core/               # [Infrastructure] Copy this folder to your new agent
│   ├── llm_client.py   # Unified API client (OpenAI, Qwen, Zhipu, etc.)
│   ├── ui_utils.py     # Notebook UI helpers (Cards, Streaming)
│   └── safe_parsing.py # Robust JSON/Code parsing
├── patterns/           # [Design Patterns] Reference implementations
│   ├── react.py        # ReAct loop controller
│   ├── reflection.py   # Reflection pattern skeleton
│   └── prompt_templates.py
├── notebooks/          # [Workbench]
│   └── debug_workbench.ipynb # Start your development here
└── config/             # [Configuration]
    └── .env.example
```

## Getting Started 

1. Copy `.env.example` to `.env` and fill in your API keys.
2. Open `notebooks/debug_workbench.ipynb` to start developing your agent.
3. Import core utilities:
   ```python
   from core import get_response, print_html
   ```

## 🚀 How to Create a New Agent

1. **Scaffold**: Create a new folder and copy core into it.
2. **Config**: Copy `.env.example` to .env and set API keys.
3. **Logic**: Create `agent_logic.py` for your Prompts and Tools.
4. **Flow**: Use `notebooks/debug_workbench.ipynb` to orchestrate the flow.

## 🛠 Features

- **Unified Client**: Switch models by changing a string (`"gpt-4o"`, `"qwen-plus"`, `"glm-4"`).
- **Visual Debugging**: `print_html` renders rich UI in notebooks for better observability.
- **Defensive Coding**: Built-in tools to handle messy LLM outputs.

