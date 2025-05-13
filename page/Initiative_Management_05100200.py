import streamlit as st
import pandas as pd
from utils.jira_utils import *
from page.Sprint import SprintSetting
from streamlit_tree_select import tree_select
from streamlit_extras.grid import grid
from streamlit_extras.row import row
import numpy as np
import streamlit_nested_layout
# st.title("Initiative Management")

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
        self.data['memberView'] = False
        if not self.data["account"] and st.session_state["account"]:
            self.data["account"] = st.session_state["account"]
        st.title("Initiative Management")

    def renderPage(self):
        if not self.jira:
            return
        if not self.data['jql'] or (not self.data['jql']['part'] and not self.data['jql']['team']):
            return
        self.data['memberView'] = False
        if self.data["account"] and self.data["account"]["org"] and self.data["account"]["org"]["part"]:
            jql = addMemberCondToJquery(IManager.jql_initiatives, self.data['jql'], True)
            self.data['memberView'] = True
        else:
            jql = addTeamCondToJquery(IManager.jql_initiatives, self.data['jql'])
        with st.expander("data"):
            self.data['memberView'] 
            jql
            self.data['jql']

        result = getIssuesByJql(self.jira, jql)
        # c1, c2 = st.columns([1, 7])
        # with c1:
        #     for i in result:
        #         self.writePageLink(i.key)
        # with c2:
        self.initiativesTable(result)

        with st.expander("row"):
            self.row_example()

    def addLabelsInGrid(self, grid, list_label):
        for i in list_label:
            grid.markdown("**{lbl}**".format(lbl=i))

    def initiativesTable(self, result):
        grid_structure = [[8, 3, 2, 2, 20] for i in range(len(result)+1)]
        i_grid = grid(*grid_structure, vertical_align="top")
        self.addLabelsInGrid(i_grid, ["Summary", "Status", "Assignee", "Due Date"])

        epic_chk = i_grid.radio("**Type Check**", ["Milestone", "Epic & Arch Review"])

        for i in result:
            # i_grid.markdown(getIssueLinkStr(i))
            i_grid.markdown(getIssueLinkStr(i, "summary"))
            i_grid.badge(**getStatusParamList(i.fields.status.name))
            i_grid.markdown(i.fields.assignee.displayName.split(" ")[0])
            i_grid.markdown(i.fields.duedate)
            if epic_chk == "Milestone":
                found, demo_epic, milestones = getMilestonesByInitiative(self.jira, i)
                if found:
                    with i_grid.expander(demo_epic.fields.summary+" ({numMilestones} milestones)".format(numMilestones=len(milestones))):
                        m_struct = [[3, 1, 1, 1, 1, 1] for i in range(len(milestones)+1)]
                        m_grid = grid(*m_struct, vertical_align="top")
                        self.addLabelsInGrid(m_grid, ["Summary", "Status", "Assignee", "Due Date", "Check1", "Check2"])
                        for m_i in range(len(milestones)-1, -1, -1):
                            m_grid.markdown(getIssueLinkStr(milestones[m_i], "summary"))
                            m_grid.badge(**getStatusParamList(milestones[m_i].fields.status.name))
                            m_grid.markdown(milestones[m_i].fields.assignee.displayName.split(" ")[0])
                            m_grid.markdown(milestones[m_i].fields.duedate)
                            m_grid.markdown("✅")
                            m_grid.markdown("✅")
                else:
                    i_grid.markdown("No milestones")
            else:   # epic case
                epics, stories = getEpicNstoriesByInitiative(self.jira, i)
                if len(epics)>0:
                    with i_grid.expander("Epics: {numEpics}".format(numEpics=len(epics))):
                        e_struct = [[9, 3, 2, 2, 15] for i in range(len(epics)+1)]

                        e_grid = grid(*e_struct, vertical_align="top")
                        self.addLabelsInGrid(e_grid, ["Summary", "Status", "Assignee", "Due Date", "Story"])

                        # key_c, summary_c, status_c, duedate_c = i_grid.columns([1, 5, 1, 1])
                        for epic in epics:
                            n_stories = len(stories[epic.key])
                            e_grid.markdown(getIssueLinkStr(epic))
                            e_grid.badge(**getStatusParamList(epic.fields.status.name))
                            e_grid.markdown(epic.fields.assignee.displayName.split(" ")[0])
                            e_grid.markdown(epic.fields.duedate)
                            if n_stories>0:
                                with e_grid.expander("Story: {numStories}".format(numStories=n_stories)):
                                    r_s = row([1, 8, 1, 1, 1])
                                    for story in stories[epic.key]:
                                        r_s.markdown(getIssueLinkStr(story))
                                        r_s.markdown(story.fields.summary)
                                        r_s.badge(**getStatusParamList(story.fields.status.name))
                                        r_s.markdown(story.fields.assignee.displayName.split(" ")[0])
                                        r_s.markdown(story.fields.duedate)
                            else:
                                e_grid.markdown("No story")
                        # if n_stories>0:
                        #     n_closed = sum(1 for i in stories[epic.key] if isStoryStatus(i, "closed"))
                        #     n_resolved = sum(1 for i in stories[epic.key] if isStoryStatus(i,"verify"))
                        #     n_open = sum(1 for i in stories[epic.key] if isStoryStatus(i,"open"))
                        #     n_inprogress = n_stories - n_open - n_resolved - n_closed
                        # else:
                        #     st.markdown("- No stories")

                        # with key_c:
                        #     st.markdown(getIssueLinkStr(epic))
                        # with summary_c:
                        #     if n_stories>0:
                        #         with st.expander(epic.fields.summary):
                        #             r_s = row([2, 5, 1, 1])
                        #             for story in stories[epic.key]:
                        #                 r_s.markdown(getIssueLinkStr(story))
                        #                 r_s.markdown(story.fields.summary)
                        #                 r_s.badge(**getStatusParamList(story.fields.status.name))
                        #                 r_s.markdown(story.fields.duedate)
                        #     else:
                        #         st.markdown(epic.fields.summary)
                        # with status_c:
                        #     st.badge(**getStatusParamList(epic.fields.status.name))
                        # with duedate_c:
                        #     st.markdown(epic.fields.duedate)
                else:
                    i_grid.markdown("No epics")
        

    def example(self):
        random_df = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

        my_grid = grid(2, [2, 4, 1], 1, 4, vertical_align="top")

        # Row 1:
        my_grid.dataframe(random_df, use_container_width=True)
        my_grid.line_chart(random_df, use_container_width=True)
        # Row 2:
        my_grid.selectbox("Select Country", ["Germany", "Italy", "Japan", "USA"])
        my_grid.text_input("Your name")
        my_grid.button("Send", use_container_width=True)
        # Row 3:
        my_grid.text_area("Your message", height=68)
        # Row 4:
        my_grid.button("Example 1", use_container_width=True)
        my_grid.button("Example 2", use_container_width=True)
        my_grid.button("Example 3", use_container_width=True)
        my_grid.button("Example 4", use_container_width=True)
        # Row 5 (uses the spec from row 1):
        with my_grid.expander("Show Filters", expanded=True):
            st.slider("Filter by Age", 0, 100, 50)
            st.slider("Filter by Height", 0.0, 2.0, 1.0)
            st.slider("Filter by Weight", 0.0, 100.0, 50.0)
        my_grid.dataframe(random_df, use_container_width=True)    
             
    def row_example(self):
        random_df = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

        row1 = row(2, vertical_align="center")
        row1.dataframe(random_df, use_container_width=True)
        row1.line_chart(random_df, use_container_width=True)

        row2 = row([2, 4, 1], vertical_align="bottom")

        row2.selectbox("Select Country", ["Germany", "Italy", "Japan", "USA"])
        row2.text_input("Your name")
        row2.button("Send", use_container_width=True)      


im = IManager()
im.renderPage()


# st.title("🐙 Streamlit-tree-select")
# st.subheader("A simple and elegant checkbox tree for Streamlit.")

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
# st.write(return_select)

