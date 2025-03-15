from openai import OpenAI
import streamlit as st 
# load environment variables from a .env file
from dotenv import load_dotenv 
# interact with the system’s environment and filesystem
import os
# store chat history
import shelve 

load_dotenv(os.getcwd() + "/openai.env")
st.title("OpenAI Chatbot UI")
USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key)

# ensure OpenAI model is initiated in session state
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"
    
# load chat history from shelve file
def load_chat_history():
    with shelve.open("chat_history") as db:
        return db.get("messages", [])
    
# save chat history to shelve file
def save_chat_history(messages):
    with shelve.open("chat_history") as db:
        db["messages"] = messages
        
# initiate or load chat history
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()
    
# sidebar with a button to delete chat history
with st.sidebar:
    if st.button("Delete Chat history"):
        st.session_state.messages = []
        save_chat_history([])
        
# display chat messages
for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar = avatar):
        st.markdown(message["content"])
        
# main chat interface
if prompt := st.chat_input("How can I help you?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar = USER_AVATAR):
        st.markdown(prompt)
        
    with st.chat_message("assistant", avatar = BOT_AVATAR):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat.completions.create(
            model = st.session_state["openai_model"],
            messages = st.session_state["messages"],
            stream = True, 
            ):
            full_response += response.choices[0].delta.content or ""
            message_placeholder.markdown(full_response + "|")
        message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    
# save chat history after each interaction
save_chat_history(st.session_state.messages)
            