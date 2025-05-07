import streamlit as st
from pymongo import MongoClient
from utils.account_util import *
from utils.db_util import *


class OrganizationSetting:
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

        self.orgs = self.db.read()
        self.sils = make_list_by_orgtype(self.orgs, '실')
        self.teams = make_list_by_orgtype(self.orgs, '팀')
        self.parts = make_list_by_orgtype(self.orgs, '파트')
        self.org_names_all = ['실 🔻'] + make_list_by_field(self.sils, 'name') + ['팀 🔻'] + make_list_by_field(self.teams, 'name') + ['파트 🔻'] + make_list_by_field(self.parts, 'name')


    def renderPage(self):
        st.title("Organization Setting")

        st.markdown("")
        operation = st.radio("🔧 Select Operation", ["Query & Edit", "Add new"], index=None)

        if not operation:
            return
        if operation == "Add new":
            self.add_new = True
        else:
            self.add_new = False

        c1, c2, c3 = st.columns([1,1,1])

        self.initDB()
        orgs = self.orgs
        org_names_all = self.org_names_all

        selected_org = None
        selected_org_name = ""

        with c1:
            with st.container(border=True):
                if self.add_new:
                    new_org = {
                        "type": st.selectbox("조직 구분", ["실", "팀", "파트"]),
                        "name": st.text_input("조직 이름", placeholder='공백 일치 필요'),
                        "leader": st.text_input("리더", placeholder="메일 아이디"),
                    }
                
                else:
                    selected_org_name = st.selectbox("🔍 Select organization to edit", org_names_all, index=None, placeholder="Click or input a name of organization")
                    selects = [selected_orgs for selected_orgs in orgs if selected_orgs['name'] == selected_org_name]
                    if len(selects)>0:
                        selected_org = selects[0]
                        new_org = {
                            "type": st.text_input("조직 구분", value = selected_org['type'], disabled=True),
                            "name": st.text_input("조직 이름", value = selected_org['name']),
                            "leader": st.text_input("리더", value = selected_org['leader'], placeholder="메일 아이디"),
                        }
                    else:
                        return
                if new_org['type'] == '팀':
                    new_org['group'] = st.text_input('JIRA 팀그룹', value = selected_org['group'] if selected_org else None, placeholder="JIRA > Issues > Search for issues > argument of membersOf function")
        with c2:
            with st.container(border=True):
                subkey, new_org[subkey] = self.displaySubpart(new_org['type'], selected_org)
        
        if new_org and subkey in new_org and len(new_org[subkey]) > 0:
            for idx in range(len(new_org[subkey])-1, -1, -1):
                if not new_org[subkey][idx]:
                    del new_org[subkey][idx]

        num = 0
        if self.add_new:
            if new_org and new_org['type'] and new_org['name'] and new_org['leader'] and st.button("Add & Save"):
                num = self.db.create(new_org)
                new_org = {}
                msg = "DB insert"
        else:
            # Save button
            if selected_org and new_org and 'name' in selected_org and selected_org['name'] and selected_org['leader'] and st.button("Save"):
                # check leader account
                num = self.db.update({'name': selected_org_name}, new_org)
                new_org = {}
                selected_org_name = ""
                msg = "DB update"
        if num:
            st.success(msg + " successful!")

        self.db.close()

    def displaySubpart(self, orgtype, org):
        if orgtype == '실':
            suborg_guide = "팀 이름 (공백까지 일치 필요)"
            subkey = 'suborg'
            label = "팀 수"
        elif orgtype == '팀':
            suborg_guide = "파트 이름 (공백까지 일치 필요)"
            subkey = 'suborg'
            label = "파트 수"
        else:
            suborg_guide = "파트원 계정 ID"
            subkey = 'members'
            label = "파트원 수"

        min = 1
        val = 1
        if org and len(org[subkey])>0:
            val = len(org[subkey])
        n_subpart = st.number_input(label, value = val, min_value=min, max_value=25, step=1)
        return subkey, [st.text_input("subpart ", key = 'subpart{i}'.format(i=idx), label_visibility = "collapsed", value = org[subkey][idx] if (org and subkey in org and idx<len(org[subkey])) else None, placeholder=suborg_guide) for idx in range(n_subpart)]

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

org_setting = OrganizationSetting()
org_setting.renderPage()
