# 🔎 GitHub Code RAG Agent — Phase 2

An agentic Code RAG application that can search and understand GitHub source code, identify functions and classes, maintain code context across follow-up questions, and retrieve recent GitHub commit history for relevant files.

## 🚀 Live Demo

https://git-rag-agent.streamlit.app/

## 📌 What Changed from Phase 1?

### Phase 1

The initial version focused on **repository-level retrieval and GitHub commit information**.

The workflow was:

```text
User
  ↓
LangGraph Agent
  ↓
Repository Search
  ↓
Relevant GitHub Repository
  ↓
GitHub REST API
  ↓
Latest 5 Commits
  ↓
OpenAI
  ↓
Final Answer
```

Phase 1 could answer questions such as:

> Find a framework for building AI agents and show me its 5 most recent commits.

### Phase 2

Phase 2 extends the system from **repository-level search** to **source-code-level understanding**.

The system now:

1. Ingests a GitHub repository
2. Filters relevant source files
3. Parses Python code using the AST
4. Creates structured code chunks
5. Generates embeddings for the code
6. Stores code, embeddings, and metadata in ChromaDB
7. Performs exact symbol retrieval for functions/classes
8. Falls back to semantic code retrieval when an exact symbol is unavailable
9. Applies structural ranking to retrieved code
10. Maintains the active repository, file, and function across follow-up questions
11. Retrieves recent GitHub commits for the relevant file
12. Uses an OpenAI model to generate the final answer

---

## 🧠 Phase 2 Code RAG

The main addition in Phase 2 is a **Code RAG pipeline**.

```text
GitHub Repository
       ↓
Repository Clone
       ↓
File Filtering
       ↓
AST Parsing
       ↓
Structured Code Chunks
       ↓
OpenAI Embeddings
       ↓
ChromaDB
       ↓
Code Retrieval
       ↓
Relevant Source Code
       ↓
LangGraph Agent
       ↓
OpenAI
       ↓
Final Answer
```

### Current LangGraph Index

The LangGraph repository was processed into:

- 274 selected files
- 257 Python files
- 17 documentation files
- 2,857 indexed chunks
- Average chunk size: approximately 23.93 lines

Large functions are divided into multiple parts while preserving metadata that allows the parts to be reconstructed.

For example, `create_react_agent` is represented by six indexed parts.

---

## 🔍 Code Retrieval

Phase 2 uses a tiered retrieval approach.

### 1. Exact Symbol Retrieval

When a user asks about a specific function or class, the system first extracts likely symbols from the query.

Example:

```text
Where is create_react_agent implemented?
```

The system identifies:

```text
create_react_agent
```

and performs an exact metadata lookup in ChromaDB.

This allows the system to retrieve the correct implementation directly instead of relying only on semantic similarity.

### 2. Semantic Retrieval

If an exact symbol cannot be identified, the system performs semantic vector search.

Example:

```text
How does LangGraph execute a graph step?
```

The system retrieves semantically relevant code and applies structural ranking to improve the results.

### 3. Structural Ranking

Retrieved code is ranked using metadata and source-code structure.

The ranking considers information such as:

- file path
- function name
- class name
- chunk type
- test/mock-related files

This helps prioritize relevant production code.

---

## 🧠 Contextual Agent State

Phase 2 introduces contextual state for code analysis.

The agent maintains:

```text
active_repo
active_file
active_function
```

This allows follow-up questions to refer to previously identified code.

For example:

```text
User:
Where is create_react_agent implemented?

Agent:
It is implemented in
chat_agent_executor.py.

User:
What changed recently in this file?

Agent:
Retrieves commits for the same file.
```

The second question does not need to repeat the repository or file path.

---

## 🛠️ Agent Tools

Phase 2 currently uses three tools.

### 1. `search_repositories`

Searches the repository knowledge base to identify relevant GitHub repositories.

### 2. `search_code`

Searches the indexed source code using:

- exact symbol matching
- semantic vector search
- structural ranking

It returns relevant source-code chunks and metadata.

### 3. `get_repository_commits`

Uses the GitHub REST API to retrieve recent commits.

It supports:

- repository-level commit retrieval
- file-specific commit retrieval

For example:

```text
Repository:
https://github.com/langchain-ai/langgraph

File:
libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py
```

The tool can retrieve commits specifically affecting that file.

---

## 🔄 Phase 2 Architecture

```text
                         USER
                           │
                           ▼
                    Streamlit UI
                           │
                           ▼
                  LangGraph Agent
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
 search_repositories   search_code   get_repository_commits
             │             │             │
             ▼             ▼             ▼
         ChromaDB       ChromaDB     GitHub REST API
                           │
                    ┌──────┴──────┐
                    │             │
             Exact Symbol    Semantic Search
                    │             │
                    └──────┬──────┘
                           ▼
                    Relevant Code
                           │
                           ▼
                         OpenAI
                           │
                           ▼
                      Final Answer
```

---

## 🧪 Phase 2 Validation

The current implementation has been tested using the LangGraph repository.

### Exact Function Retrieval

Query:

```text
Where is create_react_agent implemented?
```

The system successfully identified:

```text
Repository:
langgraph

File:
libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py

Function:
create_react_agent
```

### Code Retrieval

Query:

```text
Show me the implementation of create_react_agent.
```

The system successfully retrieved the indexed implementation from the Code RAG system.

### Semantic Retrieval

Query:

```text
How does LangGraph execute a graph step?
```

The system retrieved relevant implementation code using semantic search.

### Multi-Turn Context

Query 1:

```text
Where is create_react_agent implemented?
```

Query 2:

```text
What changed recently in this file?
```

The agent retained the repository and file context and used it to perform a file-specific GitHub commit search.

### Negative Retrieval Test

Query:

```text
Where is abcdef_random_function_123 implemented?
```

The system did not claim that the function existed and reported that it could not find the requested function.

---

## 🆚 Phase 1 vs Phase 2

| Feature | Phase 1 | Phase 2 |
|---|---|---|
| Repository search | ✅ | ✅ |
| Repository-level RAG | ✅ | ✅ |
| GitHub commit retrieval | ✅ | ✅ |
| File-level commit retrieval | ❌ | ✅ |
| Source-code ingestion | ❌ | ✅ |
| AST parsing | ❌ | ✅ |
| Structured code chunks | ❌ | ✅ |
| Code embeddings | ❌ | ✅ |
| ChromaDB code index | ❌ | ✅ |
| Exact function/class retrieval | ❌ | ✅ |
| Semantic code retrieval | ❌ | ✅ |
| Structural code ranking | ❌ | ✅ |
| Active repository context | ❌ | ✅ |
| Active file context | ❌ | ✅ |
| Active function context | ❌ | ✅ |
| Multi-turn code analysis | Limited | ✅ |
| Code-level questions | ❌ | ✅ |

---

## 🧰 Technologies

### Phase 1 + Phase 2

- Python
- Streamlit
- LangChain
- LangGraph
- ChromaDB
- OpenAI API
- GitHub REST API

### Phase 2 additions

- Python AST (`ast`) for structural source-code parsing
- OpenAI `text-embedding-3-small` for code embeddings
- Structured metadata for code retrieval and contextual reasoning

---

## 🛠️ Project Structure

```text
github-rag-agent/
│
├── app.py
│   └── Streamlit frontend
│
├── backend.py
│   ├── OpenAI integration
│   ├── ChromaDB integration
│   ├── Repository search
│   ├── Code RAG integration
│   ├── GitHub API integration
│   ├── Commit retrieval tool
│   ├── Agent state
│   └── LangGraph agent workflow
│
├── ingestion/
│   ├── Repository ingestion
│   ├── AST parsing
│   ├── Code chunking
│   └── Code indexing
│
├── requirements.txt
│   └── Python dependencies
│
├── .gitignore
│   └── Secrets and local files
│
└── README.md
    └── Project documentation
```

---

## 🔍 Example Queries

### Repository Search

```text
Find a framework for building AI agents.
```

### Code Location

```text
Where is create_react_agent implemented?
```

### Code Retrieval

```text
Show me the implementation of create_react_agent.
```

### Conceptual Code Search

```text
How does LangGraph execute a graph step?
```

### Contextual Follow-up

```text
Where is create_react_agent implemented?
```

```text
What changed recently in this file?
```

### File-Specific History

```text
What are the five most recent changes to this file?
```

---

## 🔐 Environment Variable

The application requires an OpenAI API key.

```text
OPENAI_API_KEY
```

The API key should be stored as a secret/environment variable and should never be committed to the repository.

---

## ▶️ Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Set the OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key"
```

Run the application:

```bash
streamlit run app.py
```

---

## 🎯 Phase 2 Goal

The goal of Phase 2 is to extend the original repository-level RAG system into a **source-code-aware GitHub Code RAG Agent**.

Instead of only finding repositories and their recent commits, the system can now:

- locate source-code entities
- retrieve actual implementations
- search code semantically
- use source-code structure during retrieval
- maintain code context across multiple questions
- connect retrieved code context with GitHub file history

---

## 🔮 Next Development Direction

Potential future improvements include:

1. Intent-aware retrieval for location vs implementation questions
2. More generalized structural ranking
3. More flexible symbol normalization
4. Validation using additional GitHub repositories
5. Persistent conversation/checkpoint storage
6. Improved handling of index freshness when repositories change

These improvements will be evaluated based on actual system requirements rather than added unnecessarily.

---

## 👨‍💻 Author

Afeef Zeed
