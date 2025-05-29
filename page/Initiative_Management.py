import streamlit as st
import pandas as pd
from utils.jira_utils import *
from page.Sprint import SprintSetting
from streamlit_tree_select import tree_select
from streamlit_extras.grid import grid
from streamlit_extras.row import row
import numpy as np
import streamlit_nested_layout
import copy
from datetime import datetime as dt

# st.title("Initiative Management")

class IManager:
    jql_issues_init = '''
        project=TVPLAT and ((issueType=initiative and status not in (Delivered, Closed)) or issueType in (epic, milestone) or (issueType=Story and component = _architecture)) AND summary !~ Non-Initiative AND summary !~ "Planned Q" AND created>-52w
    '''

    jql_postfix = '''
        AND ((issueType=initiative and status not in (Delivered, Closed)) or (issueType!=initiative and updated > -52w)) order by issuetype asc, duedate asc
    '''

    jql_issues_story = '''
        project=TVPLAT and (issueType in (Story, Task) AND (status !=Closed and issueType!=Story or component != _architecture)) AND summary !~ Non-Initiative AND summary !~ "Planned Q"
    '''

    jql_postfix_story = '''
        AND (updated > -52w) order by issuetype asc, duedate asc, createdDate asc
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
        self.isJiraUpdating = False

        if not self.data["account"] and st.session_state["account"]:
            self.data["account"] = st.session_state["account"]
        if self.isNeedRefreshPage():
            self.initIssueDS()
            st.session_state['il'] = []    # initiative list
            st.session_state['ml'] = []    # milestone list (not demo epic)
            st.session_state['sl'] = []    # story list
            st.session_state['el'] = []    # epic list (include demo)
            st.session_state['ded'] = {}    # demo epic dict {'initiaitve key': 'demo epic'}
            st.session_state['aed'] = {}    # arch epic dict {'initiative key': 'arch epic'}
            st.session_state['oed'] = {}    # other epics dict {'initiaitve key': ['epics']}
            st.session_state['msd'] = {}   # story dict {'epic key': [story1, story2, milestone,  ...]}
        else:
            self.il = st.session_state['il']
            self.ml = st.session_state['ml']
            self.sl = st.session_state['sl']
            self.el = st.session_state['el']
            self.ded = st.session_state['ded']
            self.aed = st.session_state['aed']
            self.oed = st.session_state['oed']
            self.msd = st.session_state['msd']

        st.title("Initiative Management")

    def isNeedRefreshPage(self):
        if not ('IManager_refreshed' in st.session_state) or not ('IManager_part' in st.session_state):
            return True
        for part_name in self.data['jql']['part']:
            if part_name not in st.session_state['IManager_part']:
                return True
        for part_name in st.session_state['IManager_part']:
            if part_name not in self.data['jql']['part']:
                return True
        return False

    def submitData(self):
        st.session_state['il'] = copy.deepcopy(self.il)
        st.session_state['ml'] = copy.deepcopy(self.ml)
        st.session_state['sl'] = copy.deepcopy(self.sl)
        st.session_state['el'] = copy.deepcopy(self.el)
        st.session_state['ded'] = copy.deepcopy(self.ded)
        st.session_state['aed'] = copy.deepcopy(self.aed)
        st.session_state['oed'] = copy.deepcopy(self.oed)
        st.session_state['msd'] = copy.deepcopy(self.msd)

    def renderPage(self):
        if not self.jira:
            return
        if not self.data['jql'] or (not self.data['jql']['part'] and not self.data['jql']['team']):
            return

        self.member_filter = False
        if self.data["account"] and self.data["account"]["org"] and self.data["account"]["org"]["part"]:
            self.member_filter = True

        if self.isNeedRefreshPage():
            self.isJiraUpdating = True
            result = self.getInitiativeEpicMilestones()

                # with st.expander("row"):
                #     self.row_example()

            self.filterByIssueType(result)
            st.session_state['IManager_refreshed'] = True
            st.session_state['IManager_part'] = self.data['jql']['part']

            self.isJiraUpdating = False

        self.renderInitiativesTable()

    def addLabelsInGrid(self, grid, list_label):
        for i in list_label:
            grid.markdown("**{lbl}**".format(lbl=i))

    def getInitiativeEpicMilestones(self):
        self.initIssueDS()
        if self.member_filter:
            jql = addMemberCondToJquery(IManager.jql_issues_init, self.data['jql'], IManager.jql_postfix, True)
        else:
            jql = addTeamCondToJquery(IManager.jql_issues_init, self.data['jql'], IManager.jql_postfix)

        print("Query for initiative >"+jql)
        return getIssuesByJql(self.jira, jql)

    def setStoriesTasksByEpics(self):
        epic_values = self.oed.values()
        epics = [epic for sublist in epic_values for epic in sublist]
        for epic in epics:
            stories = getStoriesByEpicIssue(self.jira, epic.key)
            if self.isJiraUpdating:
                print("setStory End due to jira update")
                return
            for story in stories:
                self.sl.append(story)
            self.msd[epic.key] = stories
        st.session_state['IManager_storyadded'] = True


    def initIssueDS(self):
        # lists
        self.il = []    # initiative list
        self.ml = []    # milestone list (not demo epic)
        self.sl = []    # story list
        self.el = []    # epic list (include demo)
        # dicts
        self.ded = {}    # demo epic dict {'initiaitve key': 'demo epic'}
        self.aed = {}    # arch epic dict {'initiative key': 'arch epic'}
        self.oed = {}    # other epics dict {'initiaitve key': ['epics']}
        self.msd = {}   # story dict {'epic key': [story1, story2, milestone,  ...]}
        st.session_state['IManager_storyadded'] = False
        return

    def filterByIssueType(self, result):
        if not result:
            return
        # make il, ml, sl, el, al
        for i in result:
            i_type = i.fields.issuetype.name.lower()
            if i_type == "initiative" and not (i in self.il):
                self.il.append(i)
            elif i_type == "milestone" and not (i in self.ml):
                self.ml.append(i)
            elif i_type == "epic" and not (i in self.el):
                self.el.append(i)
            else: #  (i_type == "story" or i_type == "task"):
                self.sl.append(i)
                # if str(i.fields.summary).startswith("ARCH REVIEW") and isIssueIncludeComp(i, "_architecture"):
                #     self.al.append(i)
                # else:
                #     self.el.append(i)
        
        for i in self.il:
            # set self.ded, aed, oed, msd
            self.setEpicStoriesByInitiative(i)

        self.submitData()

    def setEpicStoriesByInitiative(self, issue_initiative):
        initiative_key = issue_initiative.key
        i_links = [epic.raw for epic in issue_initiative.fields.issuelinks]

        self.ded[initiative_key] = None   # demo epic
        self.aed[initiative_key] = None   # arch review epic
        self.oed[initiative_key] = []     # other epics

        for i_link in i_links:
            if not i_link or (not 'outwardIssue' in i_link) or (not i_link['outwardIssue']):
                continue
            link_issue_key = i_link['outwardIssue']['key']
            link_type =  i_link['type']['outward']  # publishes, ..
            link_issue_sumary = i_link['outwardIssue']['fields']['summary']
            if link_type == 'publishes' and link_issue_key:
                for e_idx in range(len(self.el)):
                    e = self.el[e_idx]
                    if e.key == link_issue_key and e.fields.issuetype.name == 'Epic':
                        if link_issue_sumary.startswith("[Demo]") and isIssueIncludeComp(e, '_Sprintdemo'):
                            self.ded[initiative_key] = e
                            self.msd[e.key] = getChildIssues(e, self.ml, 'Milestone')
                        elif link_issue_sumary.startswith("ARCH REVIEW") and isIssueIncludeComp(e, '_architecture'):
                            self.aed[initiative_key] = e
                            self.msd[e.key] = getChildIssues(e, self.sl, 'Story')
                        else:
                            self.oed[initiative_key].append(e)
                            self.msd[e.key] = getChildIssues(e, self.sl, 'Story')

    def renderInitiativesTable(self):
        g = grid([15, 1], vertical_align="center")
        g.markdown("")

        grid_structure = [[1.8, 8, 1.5, 2.5, 2, 2, 20] for i in range(len(st.session_state['il'])+1)]
        i_grid = grid(*grid_structure, vertical_align="top")

        # Labels
        self.addLabelsInGrid(i_grid, ["Category", "Summary", "Status", "Assignee", "Due Date", "Progress"])
        options = ["Check result", "Demo & Milestone", "Arch Review", cNORMAL_EPIC]
        self.epic_chk = i_grid.radio("**Filter Type**", options, horizontal = True)
        if (not ("IManager_storyadded" in st.session_state) or st.session_state['IManager_storyadded'] == False) and self.epic_chk == cNORMAL_EPIC:
            print("SET story "+str(st.session_state['IManager_storyadded'])+", "+self.epic_chk)
            self.setStoriesTasksByEpics()
            pass
        else:
            print("NOT set story "+str(st.session_state['IManager_storyadded'])+", "+self.epic_chk)

        # initiative table
        for i in st.session_state['il']:
            i_grid.badge(**getFieldCategorizationParams(i))
            i_grid.markdown(getFieldSummary(i))
            i_grid.badge(**getFieldStatusToBadgeParams(i))
            i_grid.markdown(getFieldAssigneeStr(i))
            i_grid.markdown(getFieldDuedate(i))
            self.rednerProgress(i, i_grid)
            
            epic, epics = None, []
            if self.epic_chk == "Check result":
                type_str = ""
            elif self.epic_chk == "Demo & Milestone":
                type_str = "milestone(s)"
                not_exist_str = "No demo epic & milestones exist"
                epic = st.session_state['ded'][i.key]
            elif self.epic_chk == "Arch Review":
                type_str = "arch review tickets"
                not_exist_str = "No arch review tickets exist"
                epic = st.session_state['aed'][i.key]
            else:
                type_str = "epic(s)"
                not_exist_str = "No epics exist"
                epics = st.session_state['oed'][i.key]
                numEpics = len(epics) if epics else 0

            if self.epic_chk == "Check result":
                i_grid.markdown("")
                self.checkInitiative(i, i_grid)
            else:
                if self.epic_chk != cNORMAL_EPIC and epic and epic.key:
                    stories = st.session_state['msd'][epic.key]
                    numChild = len(stories)
                    if numChild > 0:
                        with i_grid.expander(getFieldSummary(epic, False) + " - {numMilestones} {type_str}".format(numMilestones=numChild, type_str=type_str)):
                            m_struct = [[3, 1, 1, 1] for i in range(2)]
                            m_grid = grid(*m_struct, vertical_align="top")
                            self.addLabelsInGrid(m_grid, ["Summary", "Status", "Assignee", "Due Date"])
                            m_grid.markdown(getFieldSummary(epic))
                            m_grid.badge(**getFieldStatusToBadgeParams(epic))
                            m_grid.markdown(getFieldAssigneeStr(epic))
                            m_grid.markdown(getFieldDuedate(epic))
                            st.markdown("< "+type_str+" >")

                            m_struct = [[3, 1, 1, 1] for i in range(numChild)]
                            m_grid = grid(*m_struct, vertical_align="top")
                            for idx in range(numChild-1, -1, -1):
                                m_grid.markdown(getFieldSummary(stories[idx]))
                                m_grid.badge(**getFieldStatusToBadgeParams(stories[idx]))
                                m_grid.markdown(getFieldAssigneeStr(stories[idx]))
                                m_grid.markdown(getFieldDuedate(stories[idx]))
                    else:
                        with i_grid.container():
                            r_e = row([3, 1, 1, 1 ])
                            r_e.markdown(getFieldSummary(epic))
                            r_e.badge(**getFieldStatusToBadgeParams(epic))
                            r_e.markdown(getFieldAssigneeStr(epic))
                            r_e.markdown(getFieldDuedate(epic))
                elif self.epic_chk != cNORMAL_EPIC:
                    i_grid.markdown(not_exist_str)

                elif self.epic_chk == cNORMAL_EPIC:   # epic case
                    if epics and numEpics > 0:
                        with i_grid.expander("Epics: {numEpics}".format(numEpics=numEpics)):
                            e_struct = [[9, 3, 2, 2, 15] for i in range(len(epics)+1)]

                            e_grid = grid(*e_struct, vertical_align="top")
                            self.addLabelsInGrid(e_grid, ["Summary", "Status", "Assignee", "Due Date", "Story"])

                            # key_c, summary_c, status_c, duedate_c = i_grid.columns([1, 5, 1, 1])
                            for epic in epics:
                                n_stories = 0
                                if epic and epic.key and st.session_state['msd'][epic.key]:
                                    stories = st.session_state['msd'][epic.key]
                                    n_stories = len(stories)
                                e_grid.markdown(getFieldSummary(epic))
                                e_grid.badge(**getFieldStatusToBadgeParams(epic))
                                e_grid.markdown(getFieldAssigneeStr(epic))
                                e_grid.markdown(getFieldDuedate(epic))
                                if n_stories > 0:
                                    with e_grid.expander("Story: {numStories}".format(numStories=n_stories)):
                                        r_s = row([8, 1, 1, 1])
                                        for story in stories:
                                            r_s.markdown(getFieldSummary(story))
                                            r_s.badge(**getFieldStatusToBadgeParams(story))
                                            r_s.markdown(getFieldAssigneeStr(story))
                                            r_s.markdown(getFieldDuedate(story))
                                else:
                                    e_grid.markdown("No stories exist")
                    else:
                        i_grid.markdown(not_exist_str)

    def checkInitiative(self, i, grid):
        
        return


    def rednerProgress(self, i, grid):
        if not i.key:
            grid.markdown("")
            return
        categorization = getField(i, "Categorization")
        demoepic = st.session_state['ded'][i.key]
        ae = st.session_state['aed'][i.key]

        total_sp, resolved_ms, n_milestones = 0, 0, 0
        if demoepic and demoepic.key and st.session_state['msd'][demoepic.key]:
            milestones = st.session_state['msd'][demoepic.key]
            n_milestones = len(milestones)
            for milestone in milestones:
                total_sp += getField(milestone, "Story Points")
                status = milestone.fields.status.name.lower()
                if status == "closed":
                   resolved_ms += 1 
        resolved = getField(i, "Story Points Info")
        # with m_grid:
        if total_sp == 0:
            p = 0
        else:
            p = round(resolved *100 / total_sp)
        grid.progress(p if p<100 else 100, "sp {r}/{t}, {p}%".format(r = round(resolved), t = round(total_sp), p = p))
            # if n_milestones == 0:
            #     m = 0
            # else:
            #     m = round(resolved_ms*100 / n_milestones)
            # st.progress(m if m<100 else 100, "milestone {r}/{t}, {p}%".format(r = resolved_ms, t = n_milestones, p = m))

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

