import streamlit as st

st.title("Organization Setting")

organizations = {
    "PCSW": {
        "label": "PC SW개발팀",
        "group": "PC SW개발팀(12101343)_grp",
        "parts": ["F/W", "Driver", "BM", "OS 솔루션"]
    },
    "MONITORSW": {
        "label": "모니터SW개발팀",
        "group": "모니터SW개발팀(11002785)_grp",
        "parts": ["제품개발1", "제품개발2", "플랫폼", "모니터 앱"]
    },
    "ITAPP": {
        "label": "IT앱솔루션개발팀",
        "group": "IT앱솔루션개발팀(11002783)_grp",
        "parts": ["시스템 APP", "Mobile APP", "AI/Data 개발"]
    },
    "ITB2B": {
        "label": "IT B2B SW개발팀",
        "group": "IT B2B SW개발팀(11002767)_grp",
        "parts": ["Cloud SW", "Client OS", "Tablet OS"]
    },
} 

st.json(organizations)

# org = {
# 	"label": "MS Product SW개발실",
#     "title": "PSW실",
# 	"leader": "sunbgin.na",
#  	"memberCount": 20,
#     "value": "psw",
# 	"upperOrg": "",
# 	"member": [],
# 	"children": [
#         {
#             "id": "PCSW",
#             "orgType": "Team",
#             "upperOrg": "PSW",
#             "leader": "jh.shin",
#             "member": [],
#             "label": "PC SW개발팀",
#             "value": "pcsw",
#             "children": [
#                 {
#                     "id": "PCFW",
#                     "orgType": "Part",
#                     "upperOrg": "PSW",
#                     "leader": "jh.shin",
#                     "member": [],
#                     "children": ["id1", "id2", "id3"],
#                     "memberCount": 20,
#                     "label": "PC F/W파트",
#                 }
#             ],
#             "memberCount": 20,
#         },
#         {
#             "id": "MONITORSW",
#             "orgType": "Team",
#             "upperOrg": "PSW",
#             "leader": "jaezoon.lee",
#             "member": [],
#             "label": "Monitor SW개발팀",
#             "value": "monitorsw",
#             "children": ["id1", "id2", "id3"],
#             "memberCount": 20,
            
            
#         },
#         {
#             "id": "ITAPP",
#             "orgType": "Team",
#             "upperOrg": "PSW",
#             "leader": "davidc.park",
#             "member": [],
#             "value": "itapp",
#             "label": "IT앱솔루션팀",
#             "children": ["id1", "id2", "id3"],
#             "memberCount": 20,
#         },
#         {
#             "id": "ITB2B",
#             "orgType": "Team",
#             "upperOrg": "PSW",
#             "leader": "witness.jung",
#             "member": [],
#             "label": "IT B2B SW개발팀",
#             "value": "itb2b",
#             "children": ["id1", "id2", "id3"],
#             "memberCount": 20,
#         }
#     ],
# }

# # return_select = tree_select(org)

# # st.title("Org Setting")
# # st.write("Query & Modify your org")
# # st.write(return_select)
# st.write(org)
