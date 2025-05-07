import streamlit as st
from utils.jira_utils import *
from page.Sprint import SprintSetting
from streamlit_tree_select import tree_select

st.title("Initiative Management")

class IManager:
    jql_initiatives = '''
        project=TVPLAT and issueType=initiative AND summary !~ Non-Initiative AND summary !~ "Planned Q"
    '''
    jql_milestones_epics = '''
        project=TVPLAT and issueType=EPIC and component = _sprintdemo
    '''
    jql_stories = '''
        project=TVPLAT and issueType=story
    '''

    def __init__(self):
        self.data = st.sidebar.data
        self.jira = st.session_state['jira']
        self.settings = st.sidebar.settings
        if not self.data["account"] and st.session_state["account"]:
            self.data["account"] = st.session_state["account"]
        with st.expander("data"):
            self.data
        with st.expander("jira"):
            self.jira

    def renderPage(self):
        if not self.jira:
            return
        if not self.data['jql'] or (not self.data['jql']['part'] and not self.data['jql']['team']):
            return

        if self.data["account"] and self.data["account"]["org"] and self.data["account"]["org"]["part"]:
            jql = addMemberCondToJquery(IManager.jql_initiatives, self.data['jql'], True)
        else:
            jql = addTeamCondToJquery(IManager.jql_initiatives, self.data['jql'])

        result = self.jira.search_issues(jql)
        # c1, c2 = st.columns([1, 7])
        # with c1:
        #     for i in result:
        #         self.writePageLink(i.key)
        # with c2:
        for i in result:
            pass
        #   self.writePageLink(i)
            # self.writePageLink(i)

    def writePageLink(self, i):
        # issue = get_issue(self.jira, i)
        st.markdown("["+i.key+"]("+i.permalink()+") "+i.fields.summary+" " +i.fields.status.name+" "+i.fields.assignee.displayName)


im = IManager()
im.renderPage()


st.title("🐙 Streamlit-tree-select")
st.subheader("A simple and elegant checkbox tree for Streamlit.")

# Create nodes to display
nodes = [
    {"label": "Folder A", "value": "folder_a"},
    {
        "label": "Folder B",
        "value": "folder_b",
        "children": [
            {"label": "Sub-folder A", "value": "sub_a"},
            {"label": "Sub-folder B", "value": "sub_b"},
            {"label": "Sub-folder C", "value": "sub_c"},
        ],
    },
    {
        "label": "Folder C",
        "value": "folder_c",
        "children": [
            {"label": "Sub-folder D", "value": "sub_d"},
            {
                "label": "Sub-folder E",
                "value": "sub_e",
                "children": [
                    {"label": "Sub-sub-folder A", "value": "sub_sub_a"},
                    {"label": "Sub-sub-folder B", "value": "sub_sub_b"},
                ],
            },
            {"label": "Sub-folder F", "value": "sub_f"},
        ],
    },
]

return_select = tree_select(nodes)
st.write(return_select)

