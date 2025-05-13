from time import sleep
from jira.client import JIRA
from jira import JIRAError

def addSprintCondToJquery(jquery, jqlinfo):
    return jquery+" AND sprint = "+jqlinfo['sprint']['name']

def addDuedateCondToJquery(jquery, jqlinfo):
    return jquery+" AND duedate <= "+jqlinfo['sprint_end']

def addSprintDuedateCondToJquery(jquery, jqlinfo):
    return jquery+" AND sprint = {sp} AND duedate <= {dd}".format(sp=jqlinfo['sprint']['name'], dd=jqlinfo['sprint_end'])

def addTeamCondToJquery(jquery, jqlinfo):
    membersOf_str = ""
    for team_name in jqlinfo["team"]:
        membersOf_str += 'membersOf("{group}"),'.format(group=jqlinfo['team'][team_name]['group'])

    # delete last comma
    if membersOf_str.endswith(","):
        membersOf_str = membersOf_str[:-1]

    return jquery+' AND assignee in ({membersOf})'.format(membersOf=membersOf_str)

def addMemberCondToJquery(jquery, jqlinfo, withLeader = False):
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

    return jquery+' AND assignee in ({cond_str})'.format(cond_str=assignee_str)

def getIssueByKey(jira, key, retry=False):
    try:
        result = jira.issue(key)
        sleep(0.1)
    except JIRAError as e:
        e
        key
        if not retry:
            sleep(1)
            getIssueByKey(jira, key)
    return result

def getIssuesByJql(jira, jql, retry=False):
    try:
        result = jira.search_issues(jql)
        sleep(0.1)
    except JIRAError as e:
        e
        if not retry:
            sleep(1)
            getIssuesByJql(jira, jql)
    return result
        
def getMilestonesByDemoepic(jira, issue_key):
    return getIssuesByJql(jira, 'project=TVPLAT and "Epic Link" ='+issue_key+" and issuetype=Milestone")

def getStoriesByEpicIssue(jira, issue_key):
    return getIssuesByJql(jira, 'project=TVPLAT and "Epic Link" ='+issue_key)
    
def getMilestonesByInitiative(jira, issue_initiative):
    result = []
    i_link = [epic.raw for epic in issue_initiative.fields.issuelinks]
    milestone_epic_found = False
    i_epic = None
    for epic_link in i_link:
        if epic_link['type']['outward'] == 'publishes' and epic_link['outwardIssue']['fields']['summary'].startswith("[Demo]"):
            i_epic = getIssueByKey(jira, epic_link['outwardIssue']['key'])
            for c in i_epic.fields.components:
                if c.name == '_Sprintdemo' and i_epic.fields.issuetype.name == 'Epic':
                    milestone_epic_found = True
                    break
            else:
                continue
            break
    if milestone_epic_found:
        if i_epic and i_epic.key:
            result = getMilestonesByDemoepic(jira, i_epic.key)
    return milestone_epic_found, i_epic, result

def getEpicNstoriesByInitiative(jira, issue_initiative):
    # returns epics excluded demo milestone
    epics = []
    stories = {}
    i_link = [epic.raw for epic in issue_initiative.fields.issuelinks]
    for epic_link in i_link:
        if epic_link['type']['outward'] == 'publishes' and not epic_link['outwardIssue']['fields']['summary'].startswith("[Demo]"):
            i_epic = getIssueByKey(jira, epic_link['outwardIssue']['key'])
            for c in i_epic.fields.components:
                if c.name == '_Sprintdemo':
                    break
            else:
                epics.append(i_epic)
                result = getStoriesByEpicIssue(jira, i_epic.key)
                if result:
                    stories[i_epic.key] = result
                else:
                    stories[i_epic.key] = []

    return epics, stories


def getIssueLinkStr(issue, label="key"):
    return "["+issue.fields.summary+"]("+issue.permalink()+")"

def getStatusParamList(status):
    statusStr = status.lower()
    if statusStr in ["in progress"]:
        return {"label": status, "color": "orange"}
    if statusStr in ["closed", "proposed to defer", "delivered", "deferred"]:
        return {"label": status, "color": "grey"}
    elif statusStr in ["approved", "ready", "resolved"]:
        return {"label": status, "color": "green"}
    elif statusStr in ["open", "screen"]:
        return {"label": status, "color": "grey"}
    else:
        return {"label": status, "color": "blue"}

def isStoryStatus(issue_story, check_status):
    issue_status = issue_story.fields.status.name.lower()
    if check_status == "closed":
        return issue_status == "closed"
    if check_status == "resolved":
        return issue_status == "verify"
    if check_status == "open":
        return issue_status in ["screen", "analysis"]

    # in progress
    return issue_status not in ["screen", "analysis", "verify", "closed"]

    
def test_jira(pwd):
    return JIRA({'server': 'http://hlm.lge.com/issue'}, basic_auth=("ybin.cho", pwd))


def test_issue(jira, key="TVPLAT-572091"):
    return jira.issue(key)

