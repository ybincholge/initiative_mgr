import json
from utils.account_util import *
from utils.tag_const import *
import streamlit as st
import base64
from pathlib import Path
from streamlit_theme import st_theme
from page.Sprint import *
from page.Organization import *

st.set_page_config(page_title="SWIM", page_icon = "📔" ,layout="wide")

class SideBar:
    def __init__(self, accUtil, sprintSetting, orgsetting):
        self.accUtil = accUtil
        self.account = accUtil.account
        self.theme = st_theme()
        self.sprint_setting = sprintSetting
        self.sprints = None
        self.sprint_names = None
        self.active_sprint = ""
        self.org_setting = orgsetting

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
            # Logo
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

            # Account part
            c1, c2 = st.columns([2, 1])
            if self.account and 'username' in self.account and self.account['username']:
                with c1:
                    st.markdown(slidebar_txt, unsafe_allow_html=True)
                    st.markdown("<p class='slidebar-text'> Hello,&ensp;"+self.username+" </p>", unsafe_allow_html=True)
                with c2:
                    st.button("Delete", on_click=self.handle_logout, use_container_width=True)

            # Sprint
            self.sprint_setting.initDB()
            self.sprints = self.sprint_setting.sprints
            self.sprint_names = self.sprint_setting.sprint_names
            self.active_sprint = self.sprint_setting.active_sprint
            self.sprint = st.selectbox('Sprint', self.sprint_names, index = self.sprint_names.index(self.active_sprint['name']))
            self.sprint_setting.db.close()

            # Organization part
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("")
                st.markdown("Organization")
            with c2:
                st.markdown("")


            self.org_setting.initDB()
            # st.multiselect("실", make_list_by_field(self.org_setting.sils, "name",)
            # self.accUtil.sls.set("org_sil", , default=self.accUtil.sls.get("org_sil")))
            # self.account["org"] = {"sil": [], "team": [], "part":[]}
            with st.container(border=True):
                if self.account and "org" in self.account and self.account["org"]:
                    selected_ss = st.multiselect("실", make_list_by_field(self.org_setting.sils, "name"), default=self.account["org"]["sil"])
                    selected_ts = st.multiselect("팀", make_list_by_field(self.org_setting.teams, "name"), default=self.account["org"]["team"])
                    selected_ps = st.multiselect("파트", make_list_by_field(self.org_setting.parts, "name"), default=self.account["org"]["part"])
                    if self.is_valid_account() and (selected_ss or selected_ts or selected_ps) and st.button("Save"):
                        self.account["org"]={"sil": selected_ss, "team": selected_ts, "part": selected_ps}
                        self.accUtil.set_account(self.account)

            self.org_setting.db.close()

            # if len(selected_ps)>0:
            #     self.accUtil.set


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

    def is_valid_account(self):
        return True if self.jira else False

    def handle_logout(self):
        self.account = self.accUtil.logout()
        st.session_state.logged_in = False

    def add_menu(self):
        im_page = st.Page("page/Initiative_Management.py", title ="📔 Initiative Management")
        ms_page = st.Page("page/Milestone_Management.py", title = "📘 Milestone Management")
        sp_page = st.Page("page/Sprint_Planning.py", title = "📆 Sprint Planning")
        sr_page = st.Page("page/Sprint_Review.py", title = "📅 Sprint Review")
        s_page = st.Page("page/Settings.py", title = "⚙️ Settings")
        so_page = st.Page("page/Organization.py", title = "⚙️ Organization Setting")
        ss_page = st.Page("page/Sprint.py", title = "⚙️ Sprint Setting")
        sl_page = st.Page("page/Labels.py")
        ac_page = st.Page("page/Account.py")

        if "logged_in" in st.session_state and st.session_state.logged_in:
            pg = st.navigation(
                {
                    "For Leader & Initiative Owner": [im_page, ms_page],
                    "For Team & Part": [sp_page, sr_page],
                    "Settings": [so_page, ss_page,] # [s_page]
                }
                # [im_page, ms_page, sp_page, sr_page, s_page]
            )
            pg.run()
        else:
            pg = st.navigation(
                {
                    "Account Setting": [ac_page]
                }
            )
            pg.run()

org_setting = OrganizationSetting()
sprint_setting = SprintSetting()
accountUtil = AccountUtil()
sidebar = SideBar(accountUtil, sprint_setting, org_setting)

sidebar.init()
sidebar.add_menu()
# sidebar.add_logo_sidebar()
