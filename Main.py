import json
from utils.account_util import *
from utils.tag_const import *
import streamlit as st

class SideBar:
    def __init__(self, accUtil):
        self.accUtil = accUtil
        self.account = accUtil.account

        if "jira" in st.session_state:
            self.jira = st.session_state['jira']
            self.username = self.jira.user(self.jira.current_user()).displayName
    
    def make_slidebar(self):
        with st.sidebar:
            c1, c2 = st.columns([2, 1])
            if self.account and self.account['user_id'] and self.account['role']:
                st.session_state.logged_in = True
                with c1:
                    st.markdown(slidebar_txt, unsafe_allow_html=True)
                    st.markdown("<p class='slidebar-text'>Hi, "+self.username+" </p>", unsafe_allow_html=True)
                with c2:
                    st.button("Delete", on_click=self.handle_logout)
            

    def init(self):
        self.make_slidebar()

    def handle_logout(self):
        self.account = self.accUtil.logout()
        st.session_state.logged_in = False

ms_page = st.Page("page/Milestone_Management.py")
sd_page = st.Page("page/Structure_Display.py")
sp_page = st.Page("page/Sprint_Planning.py")
sr_page = st.Page("page/Sprint_Review.py", title = "  Sprint Review")
so_page = st.Page("page/Organization.py")
ss_page = st.Page("page/Sprint.py")
sl_page = st.Page("page/Labels.py")
ac_page = st.Page("page/Account.py")

st.set_page_config(page_title="Initiative Management", page_icon = "📔" ,layout="wide")
sidebar = SideBar(AccountUtil())
sidebar.init()

if "logged_in" in st.session_state and st.session_state.logged_in:
    pg = st.navigation(
        {
            "📔Initiative": [ms_page, sd_page],
            "📆Sprint": [sp_page, sr_page],
            "⚙️Settings": [so_page, ss_page, sl_page]
        }
    )
    pg.run()
else:
    pg = st.navigation(
        {
            "Account Setting": [st.Page("page/Account.py")]
        }
    )

