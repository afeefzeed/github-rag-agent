import os
import requests

from typing import TypedDict, Annotated

from langchain_core.documents import Document
from langchain_core.tools import StructuredTool
from langchain_chroma import Chroma
from ingestion.search_code import search_code_tool
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from ingestion.run_ingestion import ensure_code_index

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
# =========================
# OpenAI API Key
# =========================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY is not set. "
        "Add it as an environment variable in Codespaces."
    )
ensure_code_index()

# =========================
# OpenAI Models
# =========================

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=OPENAI_API_KEY
)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY,
    temperature=0
)


# =========================
# GitHub API
# =========================

def get_commit_history(repo_url, limit=5,path=None):
    repo_path = repo_url.rstrip("/").replace(
        "https://github.com/", ""
    )


    url = f"https://api.github.com/repos/{repo_path}/commits"

    params = {"per_page": limit}

    if path:
        params["path"] = path

    response = requests.get(
        url,
        params=params,
        timeout=10,
    )
    if response.status_code != 200:
        return {"error": response.text}

    commits = response.json()

    return [
        {
            "sha": commit["sha"],
            "message": commit["commit"]["message"].split("\n")[0],
            "author": commit["commit"]["author"]["name"],
            "date": commit["commit"]["author"]["date"]
        }
        for commit in commits[:limit]
    ]

# =========================
# GitHub Commit Tool
# =========================

def get_repository_commits(repo_url: str) -> str:
    """Get the 5 most recent commits from a public GitHub repository."""

    commits = get_commit_history(repo_url, limit=5)

    if isinstance(commits, dict) and "error" in commits:
        return f"Error retrieving commits: {commits['error']}"

    result = []

    for commit in commits:
        result.append(
            f"Commit: {commit['sha'][:7]}\n"
            f"Message: {commit['message']}\n"
            f"Author: {commit['author']}\n"
            f"Date: {commit['date']}"
        )

    return "\n\n".join(result)


get_repository_commits = StructuredTool.from_function(
    func=get_repository_commits,
    name="get_repository_commits",
    description="Get the 5 most recent commits from a public GitHub repository."
)


# =========================
# Repository Knowledge Base
# =========================

repositories = [
    {
        "name": "LangChain",
        "description": "The agent engineering platform.",
        "github_url": "https://github.com/langchain-ai/langchain"
    },
    {
        "name": "LangGraph",
        "description": "Build resilient language agents as graphs.",
        "github_url": "https://github.com/langchain-ai/langgraph"
    },
    {
        "name": "Chroma",
        "description": "The AI-native open-source embedding database.",
        "github_url": "https://github.com/chroma-core/chroma"
    },
    {
        "name": "LlamaIndex",
        "description": "Data framework for LLM applications.",
        "github_url": "https://github.com/run-llama/llama_index"
    },
    {
        "name": "Qdrant",
        "description": "High-performance vector database and vector search engine.",
        "github_url": "https://github.com/qdrant/qdrant"
    },
    {
        "name": "Transformers",
        "description": "Machine learning models for text, vision, audio and multimodal applications.",
        "github_url": "https://github.com/huggingface/transformers"
    },
    {
        "name": "FAISS",
        "description": "Library for efficient similarity search and clustering of dense vectors.",
        "github_url": "https://github.com/facebookresearch/faiss"
    },
    {
        "name": "Haystack",
        "description": "Framework for production-ready LLM applications, agents and RAG pipelines.",
        "github_url": "https://github.com/deepset-ai/haystack"
    },
    {
        "name": "AutoGen",
        "description": "Programming framework for agentic AI applications.",
        "github_url": "https://github.com/microsoft/autogen"
    },
    {
        "name": "Semantic Kernel",
        "description": "SDK for integrating AI models and building AI agents and workflows.",
        "github_url": "https://github.com/microsoft/semantic-kernel"
    },
    {
        "name": "CrewAI",
        "description": "Framework for orchestrating autonomous AI agents and multi-agent workflows.",
        "github_url": "https://github.com/crewAIInc/crewAI"
    },
    {
        "name": "DSPy",
        "description": "Framework for programming and optimizing language model applications.",
        "github_url": "https://github.com/stanfordnlp/dspy"
    },
    {
        "name": "vLLM",
        "description": "High-throughput and memory-efficient inference and serving engine for large language models.",
        "github_url": "https://github.com/vllm-project/vllm"
    },
    {
        "name": "Ollama",
        "description": "Run large language models locally with a simple interface.",
        "github_url": "https://github.com/ollama/ollama"
    },
    {
        "name": "Milvus",
        "description": "Cloud-native vector database for scalable similarity search and AI applications.",
        "github_url": "https://github.com/milvus-io/milvus"
    },
    {
        "name": "Weaviate",
        "description": "Open-source vector database for AI applications and semantic search.",
        "github_url": "https://github.com/weaviate/weaviate"
    },
    {
        "name": "Elasticsearch",
        "description": "Distributed search and analytics engine.",
        "github_url": "https://github.com/elastic/elasticsearch"
    },
    {
        "name": "Open WebUI",
        "description": "Self-hosted AI interface supporting multiple large language models.",
        "github_url": "https://github.com/open-webui/open-webui"
    },
    {
        "name": "Sentence Transformers",
        "description": "Framework for sentence, text and image embeddings.",
        "github_url": "https://github.com/UKPLab/sentence-transformers"
    },
    {
        "name": "Guidance",
        "description": "Language framework for controlling large language model generation.",
        "github_url": "https://github.com/guidance-ai/guidance"
    }
]


# =========================
# ChromaDB Vector Store
# =========================

documents = []

for repo in repositories:
    content = f"""
Repository: {repo['name']}
Description: {repo['description']}
GitHub URL: {repo['github_url']}
""".strip()

    documents.append(
        Document(
            page_content=content,
            metadata={
                "name": repo["name"],
                "github_url": repo["github_url"]
            }
        )
    )


vectorstore = Chroma(
    collection_name="github_rag_app",
    embedding_function=embeddings
)

vectorstore.add_documents(documents)

# =========================
# RAG Search Tool
# =========================

def search_repositories_func(query: str) -> str:
    """Find the single most relevant GitHub repository for a user's query."""

    results = vectorstore.similarity_search(query, k=1)

    if not results:
        return "No relevant repository found."

    return results[0].page_content


search_repositories = StructuredTool.from_function(
    func=search_repositories_func,
    name="search_repositories",
    description=(
        "Find the single most relevant GitHub repository for a user's query. "
        "Returns repository name, description, and GitHub URL."
    )
)

# =========================
# LangGraph Agent
# =========================

tools = [
    search_repositories,
    search_code_tool,
    get_repository_commits
]

llm_with_tools = llm.bind_tools(tools)



class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    active_repo: str
    active_file: str
    active_function: str



def agent_node(state: AgentState):
    response = llm_with_tools.invoke(state["messages"])

    active_repo = state.get("active_repo", "")
    active_file = state.get("active_file", "")
    active_function = state.get("active_function", "")

    for message in reversed(state["messages"]):
        if hasattr(message, "name") and message.name == "search_code":
            try:
                result = message.content
                if isinstance(result, list) and result:
                    metadata = result[0].get("metadata", {})
                    active_repo = metadata.get("repository", active_repo)
                    active_file = metadata.get("file_path", active_file)
                    active_function = metadata.get("name", active_function)
            except Exception:
                pass
            break

    return {
        "messages": [response],
        "active_repo": active_repo,
        "active_file": active_file,
        "active_function": active_function,
    }


workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)

tool_node = ToolNode(tools)

def tools_node(state: AgentState):
    result = tool_node.invoke(state)

    active_repo = state.get("active_repo", "")
    active_file = state.get("active_file", "")
    active_function = state.get("active_function", "")

    for message in reversed(result["messages"]):
        if getattr(message, "name", "") == "search_code":
            try:
                
                import json

                content = message.content

                if isinstance(content, str):
                    content = json.loads(content)

                if isinstance(content, list) and content:
                    metadata = content[0].get("metadata", {})

                    active_repo = metadata.get("repository", active_repo)
                    active_file = metadata.get("file_path", active_file)
                    active_function = metadata.get("name", active_function)
            except Exception:
                pass

            break

    return {
        "messages": result["messages"],
        "active_repo": active_repo,
        "active_file": active_file,
        "active_function": active_function,
    }

workflow.add_node("tools", tools_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    tools_condition
)
workflow.add_edge("tools", "agent")

agent_graph = workflow.compile(checkpointer=memory)
