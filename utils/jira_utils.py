from time import sleep
from jira.client import JIRA
from jira import JIRAError
from utils.tag_const import *

# epic key (from story, milestone issue)
# i.raw['fields']['customfield_10434'] : 'TVPLAT-XXXXX' as epickey


cNORMAL_EPIC = "Epics"


def isValid(value):
    return value and value != noneStr and value != 0

def getChildIssues(epic, stories, issuetype = 'All'):
    child_result = []
    if not epic or not epic.key or not stories:
        return child_result
    for story in stories:
        if issuetype == 'All' or issuetype == story.fields.issuetype.name:
            if story.raw['fields']['customfield_10434'] == epic.key:
                child_result.append(story)
    
    return child_result        

def getFieldDuedate(i):
    return i.fields.duedate

def getField(i, field, print_debug = False):
    if field == "Epic Link":
        if i.raw['fields']['customfield_10434']:
            return i.raw['fields']['customfield_10434']
        else:
            return noneStr
    elif field == "Status":
        if i.fields.status and i.fields.status.name:
            return i.fields.status.name
        else:
            return noneStr
    elif field == "Categorization":
        result = i.raw['fields']['customfield_20769']
        if result and result['value']:
            return result['value']
        return noneStr
    elif field == "Story Points":
        if i.raw['fields']['customfield_10002']:
            return i.raw['fields']['customfield_10002']
        return 0
    elif field == "Story Points Info":
        storyPointsInfo = i.raw['fields']['customfield_26223']
        try:
            result = float(storyPointsInfo.split(" (Resolved")[0].split("Total : ")[1].split(" / ")[0])
            return result
        except Exception as e:
            print("exception e : "+str(e))
            return 0
    elif field == "Fix Version/s":
        if i.fields.fixVersions:
            return ",".join([v.name for v in i.fields.fixVersions])
        return noneStr
    elif field == "Grouping":
        if i.raw['fields']['customfield_15606']:
            return i.raw['fields']['customfield_15606']['value']
        else:
            return noneStr
    elif field == "Due Date":
        duedate = getFieldDuedate(i)
        if duedate:
            return duedate
        return noneStr
    elif field == "Component/s":
        if i.fields.components:
            return ",".join([v.name for v in i.fields.components])
        return noneStr
    elif field == "Release Sprint":
        if i.raw['fields']['customfield_15926']:
            return i.raw['fields']['customfield_15926'][0]
        return noneStr
    elif field == "Scope of change":
        if i.raw['fields']['customfield_15104']:
            return i.raw['fields']['customfield_15104']['value']
        return noneStr
    elif field == "Soc Dependency":
        if i.raw['fields']['customfield_19743']:
            return ",".join([v['value'] for v in i.raw['fields']['customfield_19743']])
        return noneStr
    elif field == "Controllability Risk":
        if i.raw['fields']['customfield_20802']:
            return i.raw['fields']['customfield_20802']['value']
        return noneStr
    elif field == "Estimated Effort":
        if i.raw['fields']['customfield_15244']:
            return i.raw['fields']['customfield_15244']['value']
        return noneStr
    elif field == "SRS":
        if i.raw['fields']['customfield_20754']:
            return i.raw['fields']['customfield_20754']['value']
        return noneStr
    elif field == "Development Scope":
        if i.raw['fields']['customfield_25600']:
            return ",".join([v['value'] for v in i.raw['fields']['customfield_25600']])
        return noneStr
    elif field == "Demonstration":
        if i.raw['fields']['customfield_22708']:
            return i.raw['fields']['customfield_22708']['value']
        return noneStr
    elif field == "Dev. Verification":
        if i.raw['fields']['customfield_22709']:
            return i.raw['fields']['customfield_22709']['value']
        return noneStr
    elif field == 'Status Color':
        if i.raw['fields']['customfield_15711']:
            return i.raw['fields']['customfield_15711']['value']
        return noneStr
    elif field == 'Status Summary':
        if i.raw['fields']['customfield_15710']:
            return i.raw['fields']['customfield_15710']
        return noneStr
    elif field == 'Sprint':
        if i.raw['fields']['customfield_10005']:
            return '<p>'+'</p><p>'.join([s.split("name=")[-1].split(",")[0] for s in i.raw['fields']['customfield_10005']])+"</p>"
        return ""
    elif field == 'DoD':
        if i.raw['fields']['customfield_10603']:
            return i.raw['fields']['customfield_10603']
        return noneStr
    elif field == "Description":
        if i.raw['fields']['description']:
            return '<p>' + '</p><p>'.join(i.raw['fields']['description'].split("\r\n")) + "</p>"
        return noneStr

def getStatusColor(i):
    if getField(i, "Status Color").upper() == "GREEN":
        return "🟩"
    elif getField(i, "Status Color").upper() == "YELLOW":
        return "🟨"
    elif getField(i, "Status Color").upper() == "RED":
        return "🟥"
    else:
        return ""

def isOpenStatus(i):
    return getField(i, "Status").upper() in ["DRAFTING", "SCOPING", "OPEN"]

def isReviewStatusForInitiatives(i):
    return getField(i, "Status").upper() in ["DRAFTING", "PO REVIEW", "ELT REVIEW"]

def isCompletedStatus(i):
    return getField(i, "Status").upper() in ["DELIVERED", "DEFERRED", "CLOSED"]

def isInprogressForInitiatives(i):
    return (not isOpenStatus(i)) and (not isReviewStatusForInitiatives(i)) and (not isCompletedStatus(i))

def isInprogressForMilestone(i):
    return getField(i, "Status").upper() == "IN PROGRESS"

def isOpenEpic(i):
    return getField(i, "Status").upper() in ["REVIEW", "SCOPING", "OPEN"]
def isInprogressEpic(i):
    return getField(i, "Status").upper() == "IN PROGRESS"
def isCompletedStatusEpic(i):
    return getField(i, "Status").upper() in ["DELIVERED", "DEFERRED", "CLOSED"]

def getEpicByStory(epic_dict, story, other_epic = True):
    epic_key = getField(story, "Epic Link")
    if not epic_key or not epic_dict:
        return {}

    if other_epic:
        for epics in list(epic_dict.values()):
            for epic in epics:
                if epic.key == epic_key:
                    return epic
    return None

def addSprintCondToJquery(jquery, jqlinfo):
    return jquery+" AND sprint = "+jqlinfo['sprint']['name']

def addDuedateCondToJquery(jquery, jqlinfo):
    return jquery+" AND duedate <= "+jqlinfo['sprint_end']

def addSprintDuedateCondToJquery(jquery, jqlinfo):
    return jquery+" AND sprint = {sp} AND duedate <= {dd}".format(sp=jqlinfo['sprint']['name'], dd=jqlinfo['sprint_end'])

def addTeamCondToJquery(jquery, jqlinfo, jql_postfix = ""):
    membersOf_str = ""
    for team_name in jqlinfo["team"]:
        membersOf_str += 'membersOf("{group}"),'.format(group=jqlinfo['team'][team_name]['group'])

    # delete last comma
    if membersOf_str.endswith(","):
        membersOf_str = membersOf_str[:-1]

    return jquery+' AND assignee in ({membersOf}) '.format(membersOf=membersOf_str) + jql_postfix

def addMemberCondToJquery(jquery, jqlinfo, jql_postfix = "", withLeader = False, filter_part_name = ""):
    assignee_str = ""
    jqlinfo_parts = jqlinfo['part']
    for part_name in jqlinfo_parts:
        if filter_part_name and part_name != filter_part_name:
            continue
        if withLeader:
            assignee_str += '{id},'.format(id=jqlinfo_parts[part_name]['leader'])
        for member in jqlinfo_parts[part_name]['members']:
            assignee_str += '{id},'.format(id=member)

    # delete last comma
    if assignee_str.endswith(","):
        assignee_str = assignee_str[:-1]

    return jquery+' AND assignee in ({cond_str}) '.format(cond_str=assignee_str) + jql_postfix

def getIssueByKey(jira, key, retry=0):
    try:
        result = jira.issue(key)
        sleep(0.1)
    except JIRAError as e:
        e
        key
        if retry<5:
            sleep(1)
            getIssueByKey(jira, key, retry+1)
    return result

def getIssuesByJql(jira, jql, retry=0):
    try:
        result = jira.search_issues(jql, maxResults=1000)
        sleep(0.1)
    except JIRAError as e:
        e
        if retry<5:
            sleep(1)
            getIssuesByJql(jira, jql, retry+1)
    return result
        
def getMilestonesByDemoepic(jira, issue_key):
    return getIssuesByJql(jira, 'project=TVPLAT and "Epic Link" ='+issue_key+" and issuetype=Milestone")

def getStoriesByEpicIssue(jira, issue_key):
    return getIssuesByJql(jira, 'project=TVPLAT and "Epic Link" ='+issue_key)

def isIssueIncludeComp(issue, comp):
    for c in issue.fields.components:
        if c.name == comp:
            return True
    else:
        return False

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

def getFieldSummary(i, issue_link = True):
    if issue_link:
        return "["+i.fields.summary+"]("+i.permalink()+")"
    else:
        return i.fields.summary

def getFieldKey(i, issue_link = True):
    if issue_link:
        return "["+i.key+"]("+i.permalink()+")"
    else:
        return i.key

def getLinkText(i, text):
    return "["+text+"]("+i.permalink()+")"

def getFieldAssigneeStr(i, without_id = True):
    try:
        if without_id:
            result = i.fields.assignee.displayName.split(" ")[0]
        else:
            result = i.fields.assignee.displayName
    except AttributeError as e:
        print(e)
        print("i:"+str(i)+", assignee:"+str(i.fields.assignee))
        if not i.fields.assignee:
            result = "Unassigned"
        else:
            result = str(i.fields.assignee)
    return result        

def getFieldCategorizationParams(i):
    categorization = getField(i, "Categorization")
    if categorization == "Product":
        color = "green"
    elif categorization in ["Productivity", "PoC"]:
        color = "blue"
    else:
        color = "grey"
    return {"label": categorization, "color": color}
    
def getFieldStatusToBadgeParams(i):
    status = i.fields.status.name
    statusLower = status.lower()
    if statusLower in ["in progress", "implementation"]:
        return {"label": status, "color": "orange"}
    if statusLower in ["closed", "proposed to defer", "delivered", "deferred"]:
        return {"label": status, "color": "grey"}
    elif statusLower in ["approved", "ready", "resolved"]:
        return {"label": status, "color": "green"}
    # elif statusLower in ["open", "screen"]:
    #     return {"label": status, "color": "grey"}
    else:
        return {"label": status, "color": "blue"}


def isProductCategorization(i):
    return "Product" == getField(i, "Categorization")

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

