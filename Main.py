import json
from utils.account_util import *
from utils.tag_const import *
import streamlit as st
import base64
from pathlib import Path
from streamlit_theme import st_theme

class SideBar:
    def __init__(self, accUtil):
        self.accUtil = accUtil
        self.account = accUtil.account
        self.theme = st_theme()

    def add_logo_sidebar(self):
        with st.sidebar:
            logo = f"url(data:image/png;base64,{base64.b64encode(Path(self.get_logo_path()).read_bytes()).decode()})"
            st.markdown(
                f"""
                <style>
                    [data-testid="stSidebarNav"] {{
                        background-image: {logo};
                        background-repeat: no-repeat;
                        padding-top: 90px;
                        background-position: 17px -10px;
                    }}
                </style>
                """,
                unsafe_allow_html=True,
            )

    def make_slidebar(self):
        with st.sidebar:
            logo = f"url(data:image/png;base64,{base64.b64encode(Path(self.get_logo_path()).read_bytes()).decode()})"
            st.markdown(
                f"""
                <style>
                    [data-testid="stSidebarNav"] {{
                        background-image: {logo};
                        background-repeat: no-repeat;
                        padding-top: 90px;
                        background-position: 17px -10px;
                    }}
                </style>
                """,
                unsafe_allow_html=True,
            )
            c1, c2 = st.columns([2, 1])
            if self.account and 'username' in self.account and self.account['username']:
                with c1:
                    st.markdown(slidebar_txt, unsafe_allow_html=True)
                    st.markdown("<p class='slidebar-text'> Hello,&ensp;"+self.username+" </p>", unsafe_allow_html=True)
                with c2:
                    st.button("Delete", on_click=self.handle_logout, use_container_width=True)


    def get_logo_path(self):
        try: 
            if self.theme['base'] == 'dark':
                logo_str = 'dejlogo_swim_dark.png'
            else:
                logo_str = 'dejlogo_swim_light.png'
        except:
            logo_str = 'dejlogo_swim_light.png'
        return logo_str


    def init(self):
        self.account = self.accUtil.chk_n_display_login()

        if "jira" in st.session_state:
            self.jira = st.session_state['jira']
        else:
            # Login 계정 없을때 side bar 구성
            with st.sidebar:
                st.image(self.get_logo_path(), width=350)
                
        if self.account and "username" in self.account and self.account['username']:
            self.username = self.account['username']
            self.make_slidebar()

    def handle_logout(self):
        self.account = self.accUtil.logout()
        st.session_state.logged_in = False


    def add_menu(self):
        ms_page = st.Page("page/Milestone_Management.py")
        sd_page = st.Page("page/Structure_Display.py")
        sp_page = st.Page("page/Sprint_Planning.py")
        sr_page = st.Page("page/Sprint_Review.py", title = "  Sprint Review")
        so_page = st.Page("page/Organization.py")
        ss_page = st.Page("page/Sprint.py")
        sl_page = st.Page("page/Labels.py")
        ac_page = st.Page("page/Account.py")

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
                    "Account Setting": [ac_page]
                }
            )
            pg.run()


st.set_page_config(page_title="Initiative Management", page_icon = "📔" ,layout="wide")

accountUtil = AccountUtil()
sidebar = SideBar(accountUtil)

sidebar.init()
sidebar.add_menu()
# sidebar.add_logo_sidebar()
