from time import sleep
from jira.client import JIRA
from jira import JIRAError
import threading
import queue

class JiraHandler:
    def __init__(self, jira):
        self.do_job_q = queue.Queue()
        self.handler = threading.Thread(target=self.handleApis, args=(self.do_job_q,))

    def handleApis(self, tasks):
        while True:
            job = tasks.get()
            if not job:
                break

        pass

    def addTask(self, task):
        self.do_job_q.append(task)
    
    def popTask(self):
        return self.do_job_q.pop(0)

    def getChildIssuesByEpic(self, epic, stories, issuetype = 'All'):
        child_result = []
        if not epic or not epic.key:
            return child_result
        for story in stories:
            if issuetype == 'All' or issuetype == story.fields.issuetype.name:
                if story.raw['fields']['customfield_10434'] == epic.key:
                    child_result.append(story)
        
        return child_result        

    def addSprintCondToJquery(self, jquery, jqlinfo):
        return jquery+" AND sprint = "+jqlinfo['sprint']['name']

    def addDuedateCondToJquery(self, jquery, jqlinfo):
        return jquery+" AND duedate <= "+jqlinfo['sprint_end']

    def addSprintDuedateCondToJquery(self, jquery, jqlinfo):
        return jquery+" AND sprint = {sp} AND duedate <= {dd}".format(sp=jqlinfo['sprint']['name'], dd=jqlinfo['sprint_end'])

    def addTeamCondToJquery(self, jquery, jqlinfo, jql_postfix = ""):
        membersOf_str = ""
        for team_name in jqlinfo["team"]:
            membersOf_str += 'membersOf("{group}"),'.format(group=jqlinfo['team'][team_name]['group'])

        # delete last comma
        if membersOf_str.endswith(","):
            membersOf_str = membersOf_str[:-1]

        return jquery+' AND assignee in ({membersOf}) '.format(membersOf=membersOf_str) + jql_postfix

    def addMemberCondToJquery(self, jquery, jqlinfo, jql_postfix = "", withLeader = False):
        assignee_str = ""
        jqlinfo_parts = jqlinfo['part']
        for part_name in jqlinfo_parts:
            if withLeader:
                assignee_str += '{id},'.format(id=jqlinfo_parts[part_name]['leader'])
            for member in jqlinfo_parts[part_name]['members']:
                assignee_str += '{id},'.format(id=member)

        # delete last comma
        if assignee_str.endswith(","):
            assignee_str = assignee_str[:-1]

        return jquery+' AND assignee in ({cond_str}) '.format(cond_str=assignee_str) + jql_postfix

    def getIssueByKey(self, jira, key, retry=0):
        try:
            result = jira.issue(key)
            sleep(0.1)
        except JIRAError as e:
            e
            key
            if retry<5:
                sleep(1)
                self.getIssueByKey(self, jira, key, retry+1)
        return result

    def getIssuesByJql(self, jira, jql, retry=0):
        try:
            result = jira.search_issues(jql, maxResults=2000)
            sleep(0.1)
        except JIRAError as e:
            e
            if retry<5:
                sleep(1)
                self.getIssuesByJql(self, jira, jql, retry+1)
        return result
            
    def getMilestonesByDemoepic(self, jira, issue_key):
        return self.getIssuesByJql(self, jira, 'project=TVPLAT and "Epic Link" ='+issue_key+" and issuetype=Milestone")

    def getStoriesByEpicIssue(self, jira, issue_key):
        return self.getIssuesByJql(self, jira, 'project=TVPLAT and "Epic Link" ='+issue_key)
        
    def isIssueIncludeComp(self, issue, comp):
        for c in issue.fields.components:
            if c.name == comp:
                return True
        else:
            return False

    def getEpicNstoriesByInitiative(self, jira, issue_initiative):
        # returns epics excluded demo milestone
        epics = []
        stories = {}
        i_link = [epic.raw for epic in issue_initiative.fields.issuelinks]
        for epic_link in i_link:
            if epic_link['type']['outward'] == 'publishes' and not epic_link['outwardIssue']['fields']['summary'].startswith("[Demo]"):
                i_epic = self.getIssueByKey(self, jira, epic_link['outwardIssue']['key'])
                for c in i_epic.fields.components:
                    if c.name == '_Sprintdemo':
                        break
                else:
                    epics.append(i_epic)
                    result = self.getStoriesByEpicIssue(self, jira, i_epic.key)
                    if result:
                        stories[i_epic.key] = result
                    else:
                        stories[i_epic.key] = []

        return epics, stories

    def getFieldSummary(self, i, issue_link = True):
        if issue_link:
            return "["+i.fields.summary+"]("+i.permalink()+")"
        else:
            return i.fields.summary

    def getFieldAssigneeStr(self, i, without_id = True):
        if without_id:
            return i.fields.assignee.displayName.split(" ")[0]
        return i.fields.assignee.displayName

    def getFieldStatusToBadgeParams(self, i):
        status = i.fields.status.name
        statusLower = status.lower()
        if statusLower in ["in progress"]:
            return {"label": status, "color": "orange"}
        if statusLower in ["closed", "proposed to defer", "delivered", "deferred"]:
            return {"label": status, "color": "grey"}
        elif statusLower in ["approved", "ready", "resolved"]:
            return {"label": status, "color": "green"}
        elif statusLower in ["open", "screen"]:
            return {"label": status, "color": "grey"}
        else:
            return {"label": status, "color": "blue"}

    def getFieldDuedate(self, i):
        return i.fields.duedate

    def isStoryStatus(self, issue_story, check_status):
        issue_status = issue_story.fields.status.name.lower()
        if check_status == "closed":
            return issue_status == "closed"
        if check_status == "resolved":
            return issue_status == "verify"
        if check_status == "open":
            return issue_status in ["screen", "analysis"]

        # in progress
        return issue_status not in ["screen", "analysis", "verify", "closed"]
