import os

import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_together import Together

from footer import footer
# from app2 import app2

def app():
    # Set the Streamlit page configuration and theme
    ''' st.set_page_config(
        page_title="Nyaya Mitra",
        page_icon="⚖️",  # You can replace this with a local image file or URL
        layout="centered"
    )'''

    # Display the logo image
    col1, col2, col3 = st.columns([1, 30, 1])
    with col2:
        st.image("images/human and ai.webp", use_container_width=True)

    def hide_hamburger_menu():
        st.markdown("""
            <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                
            </style>
            """, unsafe_allow_html=True)

    hide_hamburger_menu()

    # Initialize session state for messages, memory, and detailed response
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "memory" not in st.session_state:
        st.session_state.memory = ConversationBufferWindowMemory(k=2, memory_key="chat_history", return_messages=True)

    if "detailed_response" not in st.session_state:
        st.session_state.detailed_response = ""

    @st.cache_resource
    def load_embeddings():
        """Load and cache the embeddings model."""
        return HuggingFaceEmbeddings(model_name="law-ai/InLegalBERT")

    embeddings = load_embeddings()
    db = FAISS.load_local("ipc_embed_db", embeddings, allow_dangerous_deserialization=True)
    db_retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    # Prompt templates
    concise_prompt_template = """<s>[INST] As a legal chatbot specializing in the Indian Penal Code, you are tasked 
    with providing highly accurate and contextually appropriate responses. Answer only indian law related question , 
    if question is not related to indian law context then return "Please ask domain specific questions".
    CONTEXT: 
    {context}

    QUESTION: 
    {question}

    ANSWER: 
    Provide a concise and relevant answer. Avoid detailed explanations.

    </s>[INST]
    """

    brief_prompt_template = """
    <s>[INST]
    As a legal chatbot specializing in the Indian Penal Code, you are tasked with providing highly accurate and contextually appropriate responses. 
    Answer only indian law related question , if question is not related to indian law context then only return "Please ask domain specific questions" this statement only
    Ensure your answers meet these criteria:
    CONTEXT: 
    {context}

    QUESTION: 
    {question}

    ANSWER: 
    Provide a detailed and structured including:

    1. Relevant background information.

    2. Exceptions, if any.

    3. References or links for further clarification.

    </s>[INST]
    """

    concise_prompt = PromptTemplate(template=concise_prompt_template,
                                    input_variables=['context', 'question', 'chat_history'])
    brief_prompt = PromptTemplate(template=brief_prompt_template, input_variables=['context', 'question'])

    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets.get("TOGETHER_API_KEY")
        except FileNotFoundError:
            pass

    if not api_key:
        st.error("Set TOGETHER_API_KEY in the environment or Streamlit secrets.")
        st.stop()

    llm = Together(model="mistralai/Mixtral-8x22B-Instruct-v0.1", temperature=0.5, max_tokens=1024,
                   together_api_key=api_key)

    qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        memory=st.session_state.memory,
        retriever=db_retriever,
        combine_docs_chain_kwargs={'prompt': concise_prompt}
    )

    brief_qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        memory=st.session_state.memory,
        retriever=db_retriever,
        combine_docs_chain_kwargs={'prompt': brief_prompt}
    )

    def extract_answer(full_response):
        """Extracts the answer from the LLM's full response."""
        answer_start = full_response.find("Answer:")
        if answer_start != -1:
            return full_response[answer_start + len("Answer:"):].strip()
        return full_response

    def reset_conversation():
        st.session_state.messages = []
        st.session_state.memory.clear()
        st.session_state.detailed_response = ""

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Handle user input
    input_prompt = st.chat_input("Ask something...")
    if input_prompt:
        with st.chat_message("user"):
            st.markdown(f"**You:** {input_prompt}")

        st.session_state.messages.append({"role": "user", "content": input_prompt})
        with st.chat_message("assistant"):
            with st.spinner("Thinking 💡..."):
                concise_result = qa.invoke(input=input_prompt)
                concise_answer = extract_answer(concise_result["answer"])

                # Display concise response
                st.markdown(f"**Answer:** {concise_answer}")
                st.session_state.messages.append({"role": "assistant", "content": concise_answer})

                # Prepare detailed response in the background
                detailed_result = brief_qa.invoke(input=input_prompt)
                st.session_state.detailed_response = extract_answer(detailed_result["answer"])

    # Button to display the detailed response
    if st.session_state.detailed_response and st.button("📖 View Details"):
        with st.chat_message("assistant"):
            st.markdown(f"**Detailed View:** {st.session_state.detailed_response}")

    # Reset button (only visible if there are messages)
    if st.session_state.messages:
        if st.button('🗑️ Reset All Chat', on_click=reset_conversation):
            st.experimental_rerun()

    #app2()

    # Define the CSS to style the footer
    footer()
