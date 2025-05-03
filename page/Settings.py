import streamlit as st
from page.Organization import OrganizationSetting
from page.Sprint import SprintSetting

st.title("Settings")

t1, t2, t3 = st.tabs(["Organization", "Sprints", "Labels"], )

with t1:
    org_setting = OrganizationSetting()
    org_setting.renderPage()
with t2:
    sprint_setting = SprintSetting()
    sprint_setting.renderPage()    
with t3:
    st.markdown("")
    
