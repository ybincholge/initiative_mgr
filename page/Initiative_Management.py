import streamlit as st
import pandas as pd
from utils.jira_utils import *
from streamlit_tree_select import tree_select
from streamlit_extras.grid import grid
from streamlit_extras.row import row
import numpy as np
import streamlit_nested_layout
from utils.tag_const import *
import copy
from datetime import datetime as dt
import plotly.express as px

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
    jql_worklog = '''

    '''

    def __init__(self):
        self.data = st.sidebar.data
        self.jira = st.session_state['jira']
        self.settings = st.sidebar.settings
        self.data['memberView'] = False
        self.isJiraUpdating = False
        self.objName = 'IManager'

        # self.data['jql']['sprint_start']
        # self.data['jql']['sprint_end']

        # statistics
        self.initStatistics()

        if not self.data["account"] and st.session_state["account"]:
            self.data["account"] = st.session_state["account"]

        if isNeedRefreshPageByOrg(self.data, st.session_state, self.objName):
            self.initIssueDS()
            st.session_state['il'] = []    # initiative list
            st.session_state['ml'] = []    # milestone list (not demo epic)
            st.session_state['sl'] = []    # story list
            st.session_state['el'] = []    # epic list (include demo)
            st.session_state['ded'] = {}    # demo epic dict {'initiaitve key': 'demo epic'}
            st.session_state['aed'] = {}    # arch epic dict {'initiative key': 'arch epic'}
            st.session_state['oed'] = {}    # other epics dict {'initiaitve key': ['epics']}
            st.session_state['msd'] = {}    # story dict {'epic key': [story1, story2, milestone,  ...]}
            st.session_state['wld'] = {}    # worklog dict {'initiative key': [{"story": linktext, "worklogs":worklogs}}, ...]}
        else:
            self.il = st.session_state['il']
            self.ml = st.session_state['ml']
            self.sl = st.session_state['sl']
            self.el = st.session_state['el']
            self.ded = st.session_state['ded']
            self.aed = st.session_state['aed']
            self.oed = st.session_state['oed']
            self.msd = st.session_state['msd']
            self.wld = st.session_state['wld']

        self.initIssues()

    def initStatistics(self):
        if 'progressSP_Total' in st.session_state:
            self.progressSP_Total = st.session_state['progressSP_Total']
        else:
            self.progressSP_Total = st.session_state['progressSP_Total'] = 0

        if 'progressSP_Done' in st.session_state:
            self.progressSP_Done = st.session_state['progressSP_Done']
        else:
            self.progressSP_Done = st.session_state['progressSP_Done'] = 0

        if 'progreessM_Total' in st.session_state:
            self.progreessM_Total = st.session_state['progreessM_Total']
        else:
            self.progreessM_Total = st.session_state['progreessM_Total'] = 0

        if 'progreessM_Done' in st.session_state:
            self.progreessM_Done = self.progreessM_Done = st.session_state['progreessM_Done']
        else:
            self.progreessM_Done = st.session_state['progreessM_Done'] = 0

        if 'checkPassRate_NG' in st.session_state:
            self.checkPassRate_NG = st.session_state['checkPassRate_NG']
        else:
            self.checkPassRate_NG = st.session_state['checkPassRate_NG'] = 0

        if 'checkPassRate_Total' in st.session_state:
            self.checkPassRate_Total = st.session_state['checkPassRate_Total']
        else:
            self.checkPassRate_Total = st.session_state['checkPassRate_Total'] = 0

        if 'n_review_total' in st.session_state:
            self.n_review_total = st.session_state['n_review_total']
        else:
            self.n_review_total = st.session_state['n_review_total'] = 0

        if 'n_ng_review' in st.session_state:
            self.n_ng_review =  st.session_state['n_ng_review']
        else:
            self.n_ng_review =  st.session_state['n_ng_review'] = 0

        if 'ng_review_dict' in st.session_state:
            self.ng_review_dict =  st.session_state['ng_review_dict']
        else:
            self.ng_review_dict =  st.session_state['ng_review_dict'] = {}

        if 'n_ing_total' in st.session_state:
            self.n_ing_total = st.session_state['n_ing_total']
        else:
            self.n_ing_total = st.session_state['n_ing_total'] = 0

        if 'n_ng_ing' in st.session_state:
            self.n_ng_ing =  st.session_state['n_ng_ing']
        else:
            self.n_ng_ing =  st.session_state['n_ng_ing'] = 0

        if 'ng_ing_dict' in st.session_state:
            self.ng_ing_dict =  st.session_state['ng_ing_dict']
        else:
            self.ng_ing_dict =  st.session_state['ng_ing_dict'] = {}

    def submitData(self):
        st.session_state['il'] = copy.deepcopy(self.il)
        st.session_state['ml'] = copy.deepcopy(self.ml)
        st.session_state['sl'] = copy.deepcopy(self.sl)
        st.session_state['el'] = copy.deepcopy(self.el)
        st.session_state['ded'] = copy.deepcopy(self.ded)
        st.session_state['aed'] = copy.deepcopy(self.aed)
        st.session_state['oed'] = copy.deepcopy(self.oed)
        st.session_state['msd'] = copy.deepcopy(self.msd)
        st.session_state['wld'] = copy.deepcopy(self.wld)
        st.session_state['startDate'] = self.data['jql']['sprint_start']


    def initIssues(self):
        if not self.jira:
            return
        if not self.data['jql'] or (not self.data['jql']['part'] and not self.data['jql']['team']):
            return

        self.member_filter = False
        if self.data["account"] and self.data["account"]["org"] and self.data["account"]["org"]["part"]:
            self.member_filter = True

        if isNeedRefreshPageByOrg(self.data, st.session_state, self.objName):
            self.isJiraUpdating = True
            result = self.getInitiativeEpicMilestones()

                # with st.expander("row"):
                #     self.row_example()

            self.filterByIssueType(result)
            st.session_state[self.objName +'_refreshed'] = True
            st.session_state[self.objName+'_part'] = self.data['jql']['part']
            st.session_state[self.objName+'_team'] = self.data['jql']['team']
            st.session_state[self.objName+'_worklogadded'] = True

            self.isJiraUpdating = False

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

    def setWorkLogsByInitiatives(self, i):
        self.wld[i] = []
        if i in self.oed and self.oed[i]:
            epics = self.oed[i]
            if epics and len(epics)>0:
                epicKeys = "("+ ",".join([epic.key for epic in epics]) +')'
                print("[getWorkLogs] initiative: "+i+", epics_for_jql:"+epicKeys)
                issues = getWorkLogsByEpics(self.jira, epicKeys, self.data['jql']['sprint_start'], self.data['jql']['sprint_end'])
                self.wld[i] = []
                for story in issues:
                    wToken = {"story":"", "worklogs":[]}
                    wToken["story"] = getLinkText(story, story.key)
                    wToken["worklogs"] = story.fields.worklog.worklogs
                    print("wToken "+str(wToken))
                    self.wld[i].append(wToken)
                print(i+": worklogs:"+str(self.wld[i]))

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
        self.msd = {}    # story dict {'epic key': [story1, story2, milestone,  ...]}
        self.wld = {}    # worklog dict {'initiative key': [{"story": linktext, "worklogs":worklogs}}, ...]}
        st.session_state['IManager_storyadded'] = False
        st.session_state['IManager_worklogadded'] = False
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
        self.wld[initiative_key] = {}

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

        # set worklogs
        if not 'IManager_worklogadded' in st.session_state or st.session_state['IManager_worklogadded'] == False \
            or not 'startDate' in st.session_state or st.session_state['startDate'] != self.data['jql']['sprint_start']:
            self.setWorkLogsByInitiatives(initiative_key)


    def displayPage(self):
        st.title("Initiative Management")
        st.subheader("Initiative List")
        with st.expander("**Click**", expanded=True):
            grid_structure = [[1.8, 8, 1.8, 1.5, 1.8, 2.5, 20] for i in range(len(st.session_state['il'])+1)]
            i_grid = grid(*grid_structure, vertical_align="top")

            # Labels
            self.addLabelsInGrid(i_grid, ["Category", "Summary", "Status", "Assignee", "Due Date"])
            options_p = ["SP", "Milestones"]
            self.progress_chk = i_grid.radio("**Progress rate**", options_p)
            options = ["Status Color & Summary", cWORKLOG_EPIC, "Demo & Milestone", "Arch Review", cNORMAL_EPIC]
            self.epic_chk = i_grid.radio("**Filter Type**", options, horizontal = True)
            if (not ("IManager_storyadded" in st.session_state) or st.session_state['IManager_storyadded'] == False) and self.epic_chk == cNORMAL_EPIC:
                print("SET story "+str(st.session_state['IManager_storyadded'])+", "+self.epic_chk)
                self.setStoriesTasksByEpics()
                pass
            else:
                print("NOT set story "+str(st.session_state['IManager_storyadded'])+", "+self.epic_chk)
            if not 'IManager_worklogadded' in st.session_state or st.session_state['IManager_worklogadded'] == False \
                or not 'startDate' in st.session_state or st.session_state['startDate'] != self.data['jql']['sprint_start']:
                for i in st.session_state['il']:
                    self.setWorkLogsByInitiatives(i.key)
                st.session_state['wld'] = copy.deepcopy(self.wld)
                if self.data and 'jql' in self.data and self.data['jql'] and 'sprint_start' in self.data['jql'] and self.data['jql']['sprint_start']:
                    st.session_state['startDate'] = self.data['jql']['sprint_start']

            # initiative table
            self.progressSP_Total = 0
            self.progressSP_Done = 0
            self.progreessM_Total = 0
            self.progreessM_Done = 0
            self.checkPassRate_NG = 0
            self.checkPassRate_Total = 0

            for i in st.session_state['il']:
                i_grid.badge(**getFieldCategorizationParams(i))
                i_grid.markdown(getFieldSummary(i))
                i_grid.badge(**getFieldStatusToBadgeParams(i))
                i_grid.markdown(getFieldAssigneeStr(i))
                i_grid.markdown(getFieldDuedate(i))
                self.displayProgress(i, i_grid, self.progress_chk)

                epic, epics = None, []
                if self.epic_chk == "Check result" or self.epic_chk == "Status Color & Summary":
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

                self.checkInitiative(i, i_grid, self.epic_chk == "Check result")

                if self.epic_chk == 'Status Color & Summary':
                    with i_grid.expander(getFieldColor(i, "Status Color")+" Status Summary"):
                        st.text(getField(i, "Status Summary"))
                elif self.epic_chk == cWORKLOG_EPIC:            # worklog
                    # wld: worklog dict {'initiative key': [{"story": linktext, "worklogs":worklogs}}, ...]}
                    if i.key in st.session_state['wld'] and st.session_state['wld'][i.key]:
                        result = []
                        startDate = self.data['jql']['sprint_start']
                        endDate = self.data['jql']['sprint_end']
                        # to_date = dt.strptime(endDate, '%Y-%m-%d') + datetime.timedelta(days=2) # +2 days to include 주말특근
                        # endDate = to_date.strftime('%Y-%m-%d')
                        for s in st.session_state['wld'][i.key]:
                            data = sorted(s['worklogs'], key=lambda w: w.raw['started'])
                            for worklog in data:
                                w = worklog.raw
                                if startDate <= w['started'].split("T")[0] <=endDate:
                                    date = w['started'].split("T")[0]
                                    time = w['started'].split('T')[1].split(".")[0][:-3]
                                    result.append(s['story'])
                                    result.append(w['author']['displayName'].split(" ")[0])
                                    result.append(date+" "+time)
                                    result.append(w["timeSpent"])
                                    result.append("<p>"+"</p><p>".join(w["comment"].split("\r\n"))+"</p>")
                        if len(result)/5 > 0:
                            size = int(len(result)/5)
                            with i_grid.expander("workLogs {size}".format(size=size)):
                                w_struct = [[1.5, 1, 1, 1, 9] for i in range(size)] # key, author, start, duration, comment
                                w_grid = grid(*w_struct, vertical_align="top")
                                self.addLabelsInGrid(w_grid, ["Story", "Author", "Started", "T.spent", "Comment"])
                                for r in result:
                                    w_grid.markdown(r, unsafe_allow_html = True)
                        else:
                            i_grid.markdown("No worklog in "+self.data['jql']['sprint']['name'])
                    else:
                        i_grid.markdown("No worklog in "+self.data['jql']['sprint']['name'])
                else:
                    if self.epic_chk != cNORMAL_EPIC and epic and epic.key:
                        stories = st.session_state['msd'][epic.key]
                        numChild = len(stories)
                        if numChild > 0:
                            with i_grid.expander(getFieldSummary(epic, False) + " - {numMilestones} {type_str}".format(numMilestones=numChild, type_str=type_str)):
                                if self.epic_chk == "Demo & Milestone":
                                    m_struct = [[3, 1, 1, 1, 1.5, 1.5] for i in range(2)]
                                    m_grid = grid(*m_struct, vertical_align="top")
                                    self.addLabelsInGrid(m_grid, ["Summary", "Status", "Assignee", "Due Date", "Demo", "Dev. Verification"])
                                else:
                                    m_struct = [[3, 1, 1, 1] for i in range(2)]
                                    m_grid = grid(*m_struct, vertical_align="top")
                                    self.addLabelsInGrid(m_grid, ["Summary", "Status", "Assignee", "Due Date"])
                                m_grid.markdown(getFieldSummary(epic))
                                m_grid.badge(**getFieldStatusToBadgeParams(epic))
                                m_grid.markdown(getFieldAssigneeStr(epic))
                                m_grid.markdown(getFieldDuedate(epic))
                                st.markdown("< "+type_str+" >")

                                if self.epic_chk == "Demo & Milestone":
                                    m_struct = [[3, 1, 1, 1, 1.5, 1.5] for i in range(numChild)]
                                else:
                                    m_struct = [[3, 1, 1, 1] for i in range(numChild)]
                                m_grid = grid(*m_struct, vertical_align="top")
                                for idx in range(numChild-1, -1, -1):
                                    m_grid.markdown(getFieldSummary(stories[idx]))
                                    m_grid.badge(**getFieldStatusToBadgeParams(stories[idx]))
                                    m_grid.markdown(getFieldAssigneeStr(stories[idx]))
                                    m_grid.markdown(getFieldDuedate(stories[idx]))
                                    if self.epic_chk == "Demo & Milestone":
                                        # Demo, Dev. Verification
                                        m_grid.markdown(getField(stories[idx], "Demonstration"))
                                        m_grid.markdown(getField(stories[idx], "Dev. Verification"))
                    elif self.epic_chk != cNORMAL_EPIC and self.epic_chk != 'Check result' and self.epic_chk != 'Status Color & Summary':
                        i_grid.markdown(not_exist_str)

                    elif self.epic_chk == cNORMAL_EPIC:   # epic case
                        n_e_ing = 0
                        n_e_open = 0
                        n_e_close = 0

                        if epics and numEpics > 0:
                            for e in epics:
                                if isCompletedStatusEpic(e):
                                    n_e_close +=1
                                elif isInprogressEpic(e):
                                    n_e_ing += 1
                                else:
                                    n_e_open += 1

                            with i_grid.expander("Epics: {numEpics} (Open:{open}, In Progress:{ing}, Delivered:{close})".format(numEpics=numEpics, open=n_e_open, ing=n_e_ing, close=n_e_close)):
                                e_struct = [[9, 3, 2, 2, 10] for i in range(2)]
                                e_grid = grid(*e_struct, vertical_align="top")
                                self.addLabelsInGrid(e_grid, ["Summary", "Status", "Assignee", "Due Date", "Detail"])

                                # key_c, summary_c, status_c, duedate_c = i_grid.columns([1, 5, 1, 1])
                                idx = 0
                                while idx < len(epics):
                                    epic = epics[idx]
                                    n_stories = 0
                                    if epic and epic.key and st.session_state['msd'][epic.key]:
                                        stories = st.session_state['msd'][epic.key]
                                        n_stories = len(stories)
                                    e_grid.markdown(getFieldSummary(epic))
                                    e_grid.badge(**getFieldStatusToBadgeParams(epic))
                                    e_grid.markdown(getFieldAssigneeStr(epic))
                                    e_grid.markdown(getFieldDuedate(epic))
                                    with e_grid.popover("Click"):
                                        ed_struct = [[1, 5] for i in range(3)]
                                        ed_grid = grid(*ed_struct, vertical_align='top')
                                        ed_grid.markdown("Sprint")
                                        ed_grid.markdown(getField(epic, "Sprint"), unsafe_allow_html = True)
                                        ed_grid.markdown("DoD")
                                        ed_grid.markdown(getField(epic, "DoD"))
                                        ed_grid.markdown("Description")
                                        ed_grid.markdown(getField(epic, "Description"), unsafe_allow_html = True)
                                    c1, c2 = st.columns([1, 15])
                                    with c2:
                                        if n_stories > 0:
                                            with st.expander("  Story: {numStories}".format(numStories=n_stories)):
                                                rs_struct = [[6, 1.5, 1.3, 1.7, 7] for i in range(len(stories)+1)]
                                                rs_grid = grid(*rs_struct, vertical_align='top')
                                                # r_s = row([7, 1, 1, 1, 7])
                                                self.addLabelsInGrid(rs_grid, ["Summary", "Status", "Assignee", "Due Date", "Detail"])
                                                for story in stories:
                                                    rs_grid.markdown(getFieldSummary(story))
                                                    rs_grid.badge(**getFieldStatusToBadgeParams(story))
                                                    rs_grid.markdown(getFieldAssigneeStr(story))
                                                    rs_grid.markdown(getFieldDuedate(story))
                                                    with rs_grid.popover("Click", use_container_width = True):
                                                        sd_struct = [[2, 9] for i in range(3)]
                                                        sd_grid = grid(*sd_struct, vertical_align='top')
                                                        sd_grid.markdown("Sprint")
                                                        sd_grid.markdown(getField(story, "Sprint"), unsafe_allow_html = True)
                                                        sd_grid.markdown("DoD")
                                                        sd_grid.markdown(getField(story, "DoD"))
                                                        sd_grid.markdown("Description")
                                                        sd_grid.markdown(getField(story, "Description"), unsafe_allow_html = True)
                                        else:
                                            st.markdown("  No stories exist ")

                                    idx += 1
                                    e_struct = [[9, 3, 2, 2, 10] for i in range(1)]
                                    e_grid = grid(*e_struct, vertical_align="top")

                        else:
                            i_grid.markdown(not_exist_str)

        self.submitCheckResult()

        # display statistics
        self.displayStatistics()


    def submitCheckResult(self):
        if st.session_state['progressSP_Total'] != self.progressSP_Total:
            st.session_state['progressSP_Total'] = self.progressSP_Total
        if st.session_state['progressSP_Done'] != self.progressSP_Done:
            st.session_state['progressSP_Done'] = self.progressSP_Done
        if st.session_state['progreessM_Total'] != self.progreessM_Total:
            st.session_state['progreessM_Total'] = self.progreessM_Total
        if st.session_state['progreessM_Done'] != self.progreessM_Done:
            st.session_state['progreessM_Done'] = self.progreessM_Done
        if st.session_state['checkPassRate_NG'] != self.checkPassRate_NG:
            st.session_state['checkPassRate_NG'] = self.checkPassRate_NG
        if st.session_state['checkPassRate_Total'] != self.checkPassRate_Total:
            st.session_state['checkPassRate_Total'] = self.checkPassRate_Total

    def checkInitiative(self, i, grid, displayCheckResult):
        if isReviewStatusForInitiatives(i):
            checkResult = self.checkEssentialFieldForPOandELT(i)
            if displayCheckResult:
                grid.markdown("필수필드 입력 " + str(checkResult))
        elif isInprogressForInitiatives(i):
            ngExist, ngDtail = self.checkArch(i)
            ngExist2, ngDtail2 = self.checkDemoEpic(i)
            # if displayCheckResult:
            #     grid.markdown(result)
            if ngExist or ngExist2:
                self.checkPassRate_NG += 1
                self.n_ng_ing += 1
                self.ng_ing_dict[i.key] = {"issue": i, "archDetail": ngDtail, "demoDetail": ngDtail2}
        return

    def checkArch(self, i):
        # TODO
        # Due Date active sprint 포함 여부, 상태 확인 검사 추가 고려

        archiEpic = self.aed[i.key]
        changeScope = getField(i, "Scope of change")

        self.n_ing_total += 1
        self.checkPassRate_Total += 1
        ngExist = False
        ngClause = []

        if isProductCategorization(i) and "N/A" != changeScope:
            ngExist, ngDetail = self.checkArchDetail(archiEpic)
        # else:
        #     result = "✅ (Scope Of Change: "+changeScope+")"
        if ngExist:
            # result = "❌ ("+ngDetail+")"
            return True, ngDetail

        return ngExist, ""

    def checkArchDetail(self, archEpic):
        if not archEpic:
            return True, "아키리뷰 티켓 생성"

        due = getField(archEpic, "Due Date")
        isNG = False
        ngDetails = []
        prefixNGDetails = getLinkText(archEpic, "아키리뷰")+"의 "
        if not isValid(due):
            isNG = True
            ngDetails.append("Due date 설정")
        if isOpenStatus(archEpic):
            isNG = True
            ngDetails.append("Status 변경")

        if isNG:
            return isNG, prefixNGDetails+(", ".join(ngDetails))
        return isNG, ""

    def checkDemoEpic(self, i):
        demoEpic = self.ded[i.key]

        if demoEpic and demoEpic.key:
            ngExist, ngDetails = self.checkDemoEpicDetail(i, demoEpic)
            return ngExist, ngDetails
        else:
            return False, ""

    def checkDemoEpicDetail(self, initiative, demoEpic):
        iDue = getField(initiative, "Due Date")
        due = getField(demoEpic, "Due Date")

        if isCompletedStatus(demoEpic):
            return False, ""

        isNG = False
        prefixNGDetails = getLinkText(demoEpic, "Demo epic")+"의 "
        ngDetails = []
        if not isValid(due):
            isNG = True
            ngDetails.append("Due Date 설정")
        elif iDue<due:
            isNG = True
            ngDetails.append("Due Date 변경 (이니셔티브 Due Date:"+iDue+")")

        if isOpenStatus(demoEpic):
            isNG = True
            ngDetails.append("Status 변경")

        ms = self.msd[demoEpic.key]
        isInprogressMS = False
        ms_soon = None
        for milestone in ms:
            if isInprogressForMilestone(milestone):
                isInprogressMS = True
                break
            else:
                if not ms_soon:
                    ms_soon = milestone
                else:
                    if getField(milestone, "Due Date") < getField(ms_soon, "Due Date"):
                        ms_soon = milestone

        else:
            if isInprogressMS == False and ms_soon:
                isNG = True
                ngDetails.append("하위에 진행 중인 Milestone 없으므로 "+getLinkText(ms_soon, "Milestone")+"의 상태 변경, Demo 대상(Demonstration)과 검증결과 필요여부(Dev. Verification) 설정 확인")

        if not isNG:
            return False, ""

        return isNG, prefixNGDetails+(", ".join(ngDetails))

    def checkEssentialFieldForPOandELT(self, i):
        # TODO
        # 본문 parsing 및 조건 추가 고려, webOS Review Field 추가 고려

        checkResult = {
            "PO Review": "✅",
            "ELT Review": "✅",
        }

        po = {
            "Fix version/s": getField(i, "Fix Version/s"),
            "Grouping": getField(i, "Grouping"),
            "Categorization": getField(i, "Categorization")
        }

        elt = {
            "Due Date": getField(i, "Due Date"),
            "Release Sprint": getField(i, "Release Sprint"),
            "Component/s": getField(i, "Component/s"),
            "Scope Of Change": getField(i, "Scope of change"),
            "SoC Dependency": getField(i, "Soc Dependency"),
            "Controllability Risk": getField(i, "Controllability Risk"),
            "Estimated Effort": getField(i, "Estimated Effort"),
            "SRS작성필요여부": getField(i, "SRS"),
            "Development Scope": getField(i, "Development Scope"),
        }

        poNgExist, eltNgExist = False , False
        poNotClauses = []
        eltNotClauses = []

        self.n_review_total += 1
        self.checkPassRate_Total += 1
        for k in po.keys():
            if not isValid(po[k]):
               poNgExist = True
               poNotClauses.append(k)
        if poNgExist:
            checkResult['PO Review'] = "❌ ("+", ".join(poNotClauses)+")"

        if isProductCategorization(i):
            for k in elt.keys():
                if not isValid(elt[k]):
                    eltNgExist = True
                    eltNotClauses.append(k)
        else:   # PoC, Productivity, Governing, Operation, SCM
            checkFields = ["Due Date", "Release Sprint", "Component/s", "Scope Of Change"]
            for k in elt.keys():
                if k in checkFields and (not isValid(elt[k])):
                    eltNgExist = True
                    eltNotClauses.append(k)

        if eltNgExist:
            checkResult['ELT Review'] = "❌ ("+", ".join(eltNotClauses)+")"

        if poNgExist or eltNgExist:
            self.checkPassRate_NG += 1
            self.n_ng_review += 1
            self.ng_review_dict[i.key] = {"issue": i, "detail": ", ".join(poNotClauses+eltNotClauses)}

        return checkResult

    def displayStatistics(self):
        # st.session_state['progressSP_Total']
        # st.session_state['progressSP_Done']
        # st.session_state['progreessM_Total']
        # st.session_state['progreessM_Done']
        # st.session_state['checkPassRate_NG']
        # st.session_state['checkPassRate_Total']

        st.markdown("")
        # c1, c2= st.columns([1, 0.1])
        # with c1:
        st.subheader("Overall Progress")
        with st.expander("**Click**", expanded=True):
            c11, c112, c12 = st.columns([1, 0.1, 1])
            with c11:
                remain = st.session_state['progressSP_Total'] - st.session_state['progressSP_Done']
                if st.session_state['progressSP_Total'] == 0:
                    p = 0
                else:
                    p = round(st.session_state['progressSP_Done'] *100 / st.session_state['progressSP_Total'])
                st.write("Story Points")
                st.progress(p if p<100 else 100, "{p}% ({r}/{t})".format(r = round(st.session_state['progressSP_Done']), t = round(st.session_state['progressSP_Total']), p = p))
            with c12:
                remain = st.session_state['progreessM_Total'] - st.session_state['progreessM_Done']
                if st.session_state['progreessM_Total'] == 0:
                    p = 0
                else:
                    p = round(st.session_state['progreessM_Done'] * 100 / st.session_state['progreessM_Total'])
                st.write("Num. of Milestone")
                st.progress(p if p<100 else 100, "{p}% ({r}/{t})".format(r = round(st.session_state['progreessM_Done']), t = round(st.session_state['progreessM_Total']), p = p))

                # "Done": [st.session_state['progressSP_Done']],
                # "Remain": [st.session_state['progressSP_Total'] - st.session_state['progressSP_Done']]
        st.markdown("")
        st.subheader("Check rules")
        with st.expander("**Click**", expanded=True):
            c11, c12, c13 = st.columns([1, 1, 1])
            n_pass_all = self.checkPassRate_Total - self.checkPassRate_NG
            n_pass_review = self.n_review_total - self.n_ng_review
            n_pass_ing = self.n_ing_total - self.n_ng_ing

            data = {
                'state': ['Pass', 'Fail'],
                'Overall': [n_pass_all, self.checkPassRate_NG],
                'Reviewing': [n_pass_review, self.n_ng_review],
                'InProgress': [n_pass_ing, self.n_ng_ing],
                'color': ['a', 'b']
            }
            df = pd.DataFrame(data)

            with c11:
                if n_pass_all < self.checkPassRate_NG:  # 범레 표시 순서
                    torder = 'reversed'
                else:
                    torder = 'grouped'
                fig = px.pie(df, values='Overall', names = 'state', title = "Overall", height=250, width=250, color="color")
                fig.update_layout(margin=dict(l=20, r=20, t=30, b=0), legend_traceorder=torder)
                st.plotly_chart(fig, use_container_width=True, ) #, theme=None)
            with c12:
                if n_pass_review < self.n_ng_review:
                    torder = 'reversed'
                else:
                    torder = 'grouped'
                fig = px.pie(df, values='Reviewing', names = 'state', title = 'In Reviewing', height=250, width=250, color="color")
                fig.update_layout(margin=dict(l=20, r=20, t=30, b=0), legend_traceorder=torder)
                st.plotly_chart(fig, use_container_width=True, ) #, theme=None)

            with c13:
                if n_pass_ing < self.n_ng_ing:
                    torder = 'reversed'
                else:
                    torder = 'grouped'
                fig = px.pie(df, values='InProgress', names = 'state', title = 'In progress', height=250, width=250, color="color")
                fig.update_layout(margin=dict(l=20, r=20, t=30, b=0), legend_traceorder=torder)
                st.plotly_chart(fig, use_container_width=True, ) #, theme=None)

            st.markdown("")
            if self.ng_review_dict or self.ng_ing_dict:
                if self.ng_review_dict:
                    st.write("*Review 중인 과제에서,*")
                    for i in self.ng_review_dict.keys():
                        c21, c22 = st.columns([10, 1])
                        with c21:
                            st.markdown(getFieldKey(self.ng_review_dict[i]['issue'])+'는 '+self.ng_review_dict[i]['detail'] +" 설정이 필요합니다.")
                        with c22:
                            with st.popover("설정하기"):
                                archEpic = self.aed[i]
                                urlToEdit = "hlm.lge.com/issue/secure/EditIssue!default.jspa?id="+archEpic.self.split("/")[-1]
                                print("urlToEdit = "+urlToEdit)
                                st.components.v1.iframe(urlToEdit, height = 500, scrolling=True)
                if self.ng_ing_dict:
                    st.markdown("*In Progress 과제에서,*")
                    for i in self.ng_ing_dict.keys():
                        c21, c22 = st.columns([10, 1])
                        with c21:
                            if self.ng_ing_dict[i]['archDetail']:
                                if self.ng_ing_dict[i]['demoDetail']:
                                    st.markdown(getFieldKey(self.ng_ing_dict[i]['issue'])+'는 '+self.ng_ing_dict[i]['archDetail'] +"이 필요하고, "+ self.ng_ing_dict[i]['demoDetail']+"이 필요합니다.")
                                else:
                                    st.markdown(getFieldKey(self.ng_ing_dict[i]['issue'])+'는 '+self.ng_ing_dict[i]['archDetail'] +"이 필요합니다.")
                            else:
                                if self.ng_ing_dict[i]['demoDetail']:
                                    st.markdown(getFieldKey(self.ng_ing_dict[i]['issue'])+'는 '+self.ng_ing_dict[i]['demoDetail'] +"이 필요합니다.")
                                else:
                                    st.markdown(getFieldKey(self.ng_ing_dict[i]['issue'])+'는 뭐임?')

        # [st.session_state['checkPassRate_Total'] - st.session_state['checkPassRate_NG'], st.session_state['checkPassRate_Total']],
        # [st.session_state['progreessM_Done'], st.session_state['progreessM_Total'] - st.session_state['progreessM_Done']],
        pass

    def displayProgress(self, i, grid, baseType):
        if not i.key:
            grid.markdown("")
            return
        demoepic = st.session_state['ded'][i.key]
        ae = st.session_state['aed'][i.key]

        total_sp, resolved_ms, n_milestones = 0, 0, 0
        if demoepic and demoepic.key and st.session_state['msd'][demoepic.key]:
            milestones = st.session_state['msd'][demoepic.key]
            n_milestones = len(milestones)

            for milestone in milestones:
                milestone_sp = getField(milestone, "Story Points")
                total_sp += milestone_sp
                status = milestone.fields.status.name.lower()
                if status == "closed":
                   resolved_ms += 1

        # ["Story Points", "Milestone"]
        ## baseType: SP case
        resolved = getField(i, "Story Points Info")

        self.progressSP_Total += total_sp
        self.progressSP_Done += resolved
        ## baseType: Milestone case
        self.progreessM_Total += n_milestones
        self.progreessM_Done += resolved_ms

        if baseType == "SP":
            if total_sp == 0:
                p = 0
            else:
                p = round(resolved *100 / total_sp)
            grid.progress(p if p<100 else 100, "{p}% ({r}/{t})".format(r = round(resolved), t = round(total_sp), p = p))
        else: # milestones
            if n_milestones == 0:
                m = 0
            else:
                m = round(resolved_ms*100 / n_milestones)
            grid.progress(m if m<100 else 100, "{p}% ({r}/{t})".format(r = resolved_ms, t = n_milestones, p = m))


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
im.displayPage()

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

