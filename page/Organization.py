import streamlit as st
from pymongo import MongoClient
from utils.account_util import *
from utils.st_util import *

st.markdown("")

client = MongoClient("10.157.75.217", 27017)

db = client["iMgr"]

# orgs = list(db.org.find())

# def make_selectbox_names(org, add_all=False, add_None=False):
#     names = [o['name'] for o in org]
#     if add_all:
#         names.append("전체")
#     if add_None:
#         return ["-"] + names

#     return names

# def get_list(query):
#     return list(db['org'].find(query))

# def get_filtered_list_n_names(org_list, name_to_search, add_all):
#     if org_list and name_to_search:
#         filtered_list = [e for e in org_list if 'name' in e and e['name'] == name_to_search]
#         filtered_names = make_selectbox_names(filtered_list, add_all)
#         return filtered_list, filtered_names
#     else:
#         return [], []


st.title("🏢 Organization Setting")
st.subheader("Select Organization to edit or view in detail")


#st.write(return_select)
# list_orgs = [{"label": k['name'], "value": k['name'], "children": (k['suborg'] if 'suborg' in k and k['suborg'] else []) } for k in orgs if 'name' in k and k['name']]
# json_orgs = json.dumps(list_orgs)

# st.write("# list")
# list_orgs
# st.write("## tree")
# selected_org = tree_select(list_orgs)
# st.write("# json")
# json_orgs

# st.write("## tree")
# selected_org = tree_select(json_orgs)
# # st.write(selected_org)

# def org_selects():

#     sils = get_list({'type': '실'})
#     sil_names = make_selectbox_names(sils, False, True)
    
#     teams = get_list({'type': '팀'})
#     # team_names = make_selectbox_names(teams)
    
#     parts = get_list({'type': '파트'})
#     part_names = make_selectbox_names(parts)
    
#     c1, c2, c3, c4 = st.columns([1, 1, 1, 5])
#     container = st.container(border=True)
#     on_change_sil = None
#     selected_name = ""

#     def on_change_sil(selected_name):
#         selected_name = st.session_state['sil']
#         if selected_name and selected_name != "-":
#             selected_org, b = get_filtered_list_n_names(sils, selected_name,  False)
#             if 'name' in selected_org and selected_org['name'] and selected_name != "-":
#                 st.write("sil selected: "+str(selected_org))

#         if 'suborg' in selected_org and selected_org['suborg']:
#             selected_name = st.selectbox("팀", ["-"]+selected_org['suborg'])
#         else:
#             selected_name = st.selectbox("팀", ["-"])
            
#         return selected_name

#     with st.container(border=True):
#         with c1:
#             selected_name = st.selectbox("실", sil_names, index=0,on_change=on_change_sil, key='sil')
#         with c2:
#             selected_name = on_change_sil(selected_name)
#         with c3:
#             def on_change_team(selected_name):
#                 print("on_change_team selected name : "+selected_name)

#                 selected_org = {'suborg': []}

#                 if selected_name and selected_name != "-":
#                     selected_org, b = get_filtered_list_n_names(sils, selected_name,  False)
#                     if 'name' in selected_org and selected_org['name'] and selected_name != "-":
#                         st.write(str(selected_org))
#                 if 'suborg' in selected_org and selected_org['suborg']:
#                     selected_name = st.selectbox("파트", ["-"]+selected_org['suborg'])
#                 else:
#                     selected_name = st.selectbox("파트", ["-"])
#                 return selected_name
#             selected_name = on_change_team(selected_name)


    # c1, c2 = st.columns(2)
    # with c1:
    #     c1, c2, c3 = st.columns(3)
    #     with c1:
    #         sil = st.selectbox("실", make_selectbox_names(get_list("sil"), False), 0)
    #     with c2:
    #         team = st.selectbox("팀", make_selectbox_names(teams, True), 0, on_change=on_change_team, key='team')
    #     with c3:
    #         part = st.selectbox("파트", make_selectbox_names(parts, True), 0, on_change=on_change_part, key='part')


    
# org_selects()


# part = db.part

# part.insert_many([
#     {
#         "id": "pdevel1",
#         "name": "제품개발1파트",
#         "type" : "파트",
#         "leader": "kwangwon.lee",
#         "members": ["hb.jang", "hw.kim", "namyun.kim", "pacey.park"]
#     },
#     {
#         "id": "pdevel2",
#         "name": "제품개발2파트",
#         "type" : "파트",
#         "leader": "heesong.lee",
#         "members": ["robin.kang", "hanseok.bae", "minho.heo", "sungsig.yoon", "jinju.kim", "yeonwoo.park"]
#     },
#     {
#         "id": "platform",
#         "name": "플랫폼파트",
#         "type" : "파트",
#         "leader": "yongduck.cho",
#         "members": ["yongsoo.lee", "daehyun.cho", "ghwan.lee", "hyunwook47.park"]
#     },
#     {
#         "id": "monitorapp",
#         "name": "모니터앱파트",
#         "type" : "파트",
#         "leader": "seunghee.seo1215",
#         "members": ["hyungsuk0305.lee", "sunghoon419.cho"]
#     },
#     {
#         "id": "pcfw",
#         "name": "F/W 파트",
#         "type" : "파트",
#         "leader": "sungjae.roh",
#         "members": [
#             "bs.koh", "superty.lee", "namjin.lee", "jongho3.choi", "jm1102.kang",
#             "jihan1030.kim", "donggu.kyung", "jieon.kang", "sumyeong.kim", "seungjun.hong"
#         ]
#     },
#     {
#         "id": "pcdriver",
#         "name": "Driver 파트",
#         "type" : "파트",
#         "leader": "sangkilsk.lee",
#         "members": ["minsu9.kim", "seungjun.park", "hanmun.ryu", "jaeho.min", "daeseob.shin"]
#     },
#     {
#         "id": "pcbm",
#         "name": "BM 파트",
#         "type" : "파트",
#         "leader": "jongik1.kim",
#         "members": [
#             "seokhyun.you", "kris.ko", "doug.kim", "saudi.kim", "jeongmin.park",
#             "daewon.seo", "icarus.seo", "yongmook.choi"
#         ]
#     },
#     {
#         "id": "ossolution",
#         "name": "OS솔루션파트",
#         "type" : "파트",
#         "leader": "daewoong.lim",
#         "members": ["kiung.kim", "dangwoo.choi", "sejin.kim", "tobie.park", "gwiro.lee", "hwayeun.lee", "ohjoon.kwon"]
#     },
#     {
#         "id": "itsystemapp",
#         "name": "시스템APP개발",
#         "type" : "파트",
#         "leader": "jeehan.yun",
#         "members": ["junghoon10.park", "seungbong.choi", "js21.park", "teaho.kim", "junwoo.ha", "yongbok.choi", "daeyeop.kim"]
#     },
#     {
#         "id": "itmobileapp",
#         "name": "MobileAPP개발",
#         "type" : "파트",
#         "leader": "daehwan.lee",
#         "members": ["nr.seo", "donghoon.kim", "jonggon.oh", "jaesik.lim", "woochan4759.son", "hwanil.yoo"]
#     },
#     {
#         "id": "itaidata",
#         "name": "AI/Data개발",
#         "type" : "파트",
#         "leader": "hs.moon",
#         "members": ["sangho.yoon", "kitak.moon", "woonchae.lee", "sungbo.lim", "changjun.yeo", "seunghwan91.lee"]
#     },
#     {
#         "id": "cloudsw",
#         "name": "Cloud SW파트",
#         "type" : "파트",
#         "leader": "jaesuk.kim",
#         "members": ["youngjin1.seo", "sanghwa.yu", "jaejun.min", "jung.youngjin"]
#     },
#     {
#         "id": "clientos",
#         "name": "Client OS파트",
#         "type" : "파트",
#         "leader": "donghun.yoon",
#         "members": ["mike.seo", "donghyeon.seo", "myeonghwan.gong"]
#     },
#     {
#         "id": "tabletos",
#         "name": "Tablet ODM파트",
#         "type" : "파트",
#         "leader": "donhee.nam",
#         "members": ["bina.lee", "younggyu.joo"]
#     }
# ])