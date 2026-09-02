# 🔎 GitHub RAG Agent

An agentic RAG application that uses semantic search and the GitHub API to find relevant GitHub repositories and retrieve their latest commit history.

🚀 Live Demo

https://git-rag-agent.streamlit.app/

📌 What It Does

The application allows users to ask natural-language questions such as:

> Find a Python framework for AI agents and show me its 5 most recent commits.

The agent:

1. Understands the user's request
2. Searches a repository knowledge base using semantic similarity
3. Selects the most relevant GitHub repository
4. Retrieves the latest 5 commits using the GitHub API
5. Generates a structured response using an OpenAI model

## 🏗️ Architecture


User
  ↓
Streamlit UI
  ↓
LangGraph Agent
  ↓
ChromaDB Semantic Search
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


🧠 Technologies

* Python
* Streamlit
* LangChain
* LangGraph
* ChromaDB
* OpenAI API
* GitHub REST API

🛠️ Project Structure

github-rag-agent/
│
├── app.py              # Streamlit frontend
├── backend.py          # RAG pipeline and LangGraph agent
├── requirements.txt    # Python dependencies
├── .gitignore          # Ignored files and secrets
└── README.md           # Project documentation


🔍 Example Queries


Find a vector database for AI applications and show me its 5 most recent commits.

Find a framework for building AI agents and give me its GitHub URL.

Find a library for generating text embeddings and show me its 5 most recent commits.


 🔐 Environment Variable

The application requires an OpenAI API key.


OPENAI_API_KEY

The API key should be stored as a secret/environment variable and should never be committed to the repository.


▶️ Run Locally

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

🎯 Project Goal

This project demonstrates how Retrieval-Augmented Generation (RAG), agentic workflows, vector databases, and external APIs can be combined into a practical AI application.

👨‍💻 Author

Afeef Zeed
