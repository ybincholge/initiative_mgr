import streamlit as st


st.title("Initiative Management")

class IManager:
    def __init__(self):
        if "jira" in st.session_state:
            self.jira = st.session_state['jira']
        
        

