from utils.db_util import *

class OrganizationUtil:
    def __init__(self):
        self.db = None

        # if "db_org" in st.session_state and st.session_state['db_org']:
        #     self.db = st.session_state["db_org"]
        # else:
        #     self.db = DBUtil('org')
        #     st.session_state["db_org"] = self.db
        self.orgs = None
        self.sils = None
        self.teams = None
        self.parts = None
        self.org_names_all = None

    def initDB(self):
        if not self.db:
            self.db = DBUtil('org')
            self.dbOpened = True

        self.orgs = self.db.read()
        self.sils = make_list_by_orgtype(self.orgs, '실')
        self.teams = make_list_by_orgtype(self.orgs, '팀')
        self.parts = make_list_by_orgtype(self.orgs, '파트')
        self.org_names_all = ['실 🔻'] + make_list_by_field(self.sils, 'name') + ['팀 🔻'] + make_list_by_field(self.teams, 'name') + ['파트 🔻'] + make_list_by_field(self.parts, 'name')

    def closeDB(self):
        self.db.close()
        self.db = None
        self.dbOpened = False

    def getOrgFromName(self, name, src_list=None):
        if src_list:
            orgs = src_list
        else:
            orgs = self.orgs
        for org in orgs:
            if org['name'] == name:
                return org
        return None

    def getJqlConditionByOrg(self, org_str):
        if not org_str:
            return ""

        org = self.getOrgFromName(org_str)
        result_teams = {}
        result_parts = {}
        org_type = org['type']
        
        def add_part(part_name):
            part = self.getOrgFromName(part_name, self.parts)
            print("part_org "+str(part))
            result_parts[part_name] = {"leader": part['leader'], 'members': []+part['members']}

        def add_team(team_name):
            team = self.getOrgFromName(team_name, self.teams)
            result_teams[team_name] = {"leader": team['leader']}
            if team and 'group' in team and team['group']:
                result_teams[team_name]['group'] = team['group']
                if team and 'suborg' in team and len(team['suborg'])>0:
                    for part_name in team['suborg']:
                        if part_name not in result_parts:
                            add_part(part_name)
                else:
                    st.write('need to check ', team)
            else:
                st.write('need to check ', team)

        if org_type == "실":
            print(org_str+" 실 case")
            for team_name in org['suborg']:
                add_team(team_name)

        if org_type == '팀':
            print(org_str+" 팀 case")
            add_team(org_str)

        if org_type == '파트':
            print(org_str+" 파트 case")
            add_part(org_str)

        return result_teams, result_parts
