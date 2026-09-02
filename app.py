import streamlit as st
from langchain_core.messages import HumanMessage
import backend


st.set_page_config(
    page_title="GitHub RAG Agent",
    page_icon="🔎",
    layout="centered"
)


st.title("🔎 GitHub RAG Agent")

st.write(
    "Ask questions about GitHub repositories. "
    "The AI agent uses RAG and the GitHub API "
    "to find repositories and retrieve recent commits."
)


question = st.text_area(
    "Ask your question:",
    placeholder=(
        "Example: Find a Python framework for AI agents "
        "and show me its 5 most recent commits."
    ),
    height=120
)


if st.button("Ask Agent", type="primary"):

    if not question.strip():
        st.warning("Please enter a question.")

    else:
        with st.spinner("Agent is researching GitHub..."):

            result = backend.agent_graph.invoke({
                "messages": [
                    HumanMessage(content=question)
                ]
            })

        answer = result["messages"][-1].content

        st.subheader("Answer")
        st.markdown(answer)


st.divider()

st.caption(
    "Powered by LangGraph • LangChain • ChromaDB • OpenAI • GitHub API"
)
