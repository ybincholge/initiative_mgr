from time import sleep

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

def get_issue(jira, key):
    result = jira.issue(key)
    sleep(0.1)
    return result
    
