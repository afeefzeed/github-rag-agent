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


# Initialize visible chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# Display previous conversation
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


question = st.chat_input(
    "Ask a question about GitHub repositories..."
)


if question:

    # Display user's new question
    with st.chat_message("user"):
        st.markdown(question)

    # Save user's question to visible history
    st.session_state.chat_history.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("assistant"):
        with st.spinner("Agent is researching GitHub..."):

            if "thread_id" not in st.session_state:
                st.session_state.thread_id = "streamlit-user-1"

            result = backend.agent_graph.invoke(
                {
                    "messages": [
                        HumanMessage(content=question)
                    ]
                },
                config={
                    "configurable": {
                        "thread_id": st.session_state.thread_id
                    }
                }
            )

            answer = result["messages"][-1].content

        st.markdown(answer)

    # Save assistant's answer to visible history
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": answer
    })


st.divider()

st.caption(
    "Powered by LangGraph • LangChain • ChromaDB • OpenAI • GitHub API"
)