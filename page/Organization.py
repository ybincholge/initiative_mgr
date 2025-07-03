import streamlit as st
from utils.org_util import *


class OrganizationSetting:
    def __init__(self):
        self.orgUtil = OrganizationUtil()

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

        c1, c2, c3 = st.columns([1,1,0.5])

        self.orgUtil.initDB()
        orgs = self.orgUtil.orgs
        org_names_all = self.orgUtil.org_names_all

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
                num = self.orgUtil.db.create(new_org)
                new_org = {}
                msg = "DB insert"
        else:
            # Save button
            if selected_org and new_org and 'name' in selected_org and selected_org['name'] and selected_org['leader'] and st.button("Save"):
                # check leader account
                num = self.orgUtil.db.update({'name': selected_org_name}, new_org)
                new_org = {}
                selected_org_name = ""
                msg = "DB update"
        if num:
            st.success(msg + " successful!")

        self.orgUtil.db.close()

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

org_setting = OrganizationSetting()
org_setting.renderPage()
