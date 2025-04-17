import streamlit as st
from streamlit_tree_select import tree_select

org = {
	"label": "MS Product SW개발실",
    "title": "PSW실",
	"leader": "sunbgin.na",
 	"memberCount": 20,
    "value": "psw",
	"upperOrg": "",
	"member": [],
	"children": [
        {
            "id": "PCSW",
            "orgType": "Team",
            "upperOrg": "PSW",
            "leader": "jh.shin",
            "member": [],
            "label": "PC SW개발팀",
            "value": "pcsw",
            "children": [
                {
                    "id": "PCFW",
                    "orgType": "Part",
                    "upperOrg": "PSW",
                    "leader": "jh.shin",
                    "member": [],
                    "children": ["id1", "id2", "id3"],
                    "memberCount": 20,
                    "label": "PC F/W파트",
                }
            ],
            "memberCount": 20,
        },
        {
            "id": "MONITORSW",
            "orgType": "Team",
            "upperOrg": "PSW",
            "leader": "jaezoon.lee",
            "member": [],
            "label": "Monitor SW개발팀",
            "value": "monitorsw",
            "children": ["id1", "id2", "id3"],
            "memberCount": 20,
            
            
        },
        {
            "id": "ITAPP",
            "orgType": "Team",
            "upperOrg": "PSW",
            "leader": "davidc.park",
            "member": [],
            "value": "itapp",
            "label": "IT앱솔루션팀",
            "children": ["id1", "id2", "id3"],
            "memberCount": 20,
        },
        {
            "id": "ITB2B",
            "orgType": "Team",
            "upperOrg": "PSW",
            "leader": "witness.jung",
            "member": [],
            "label": "IT B2B SW개발팀",
            "value": "itb2b",
            "children": ["id1", "id2", "id3"],
            "memberCount": 20,
        }
    ],
}

# return_select = tree_select(org)

# st.title("Org Setting")
# st.write("Query & Modify your org")
# st.write(return_select)
st.write(org)
