import streamlit as st
from datetime import datetime as dt
from utils.db_util import *

class SprintSetting:
    def __init__(self):
        self.db = None
        self.now = dt.now()
        self.year = self.now.year
        self.active_sprint = ""

    def initDB(self):
        self.db = DBUtil('sprint')
        self.sprints_all = self.db.read({})
        self.updateSprintInfo()

    def updateSprintInfo(self):
        self.sprints = make_list_by_field_condition(self.sprints_all, "name", str(self.year), "startswith")
        self.sprint_names = make_list_by_field(self.sprints, "name")
        self.active_sprint = self.current_sprint = self.findActiveSprint()

    def renderPage(self):
        st.title("Sprint Setting")
        st.markdown("")
        self.initDB()
        c1, c2, c3 = st.columns([1, 2, 2])
        with c1:
            years = [self.year-1, self.year, self.year+1]
            self.year = st.selectbox("연도 선택", [self.year-1, self.year, self.year+1], index=years.index(self.now.year))
        with c2:
            self.updateSprintInfo()
            selected_sprint_name = st.selectbox("Select a sprint", self.sprint_names, index=self.sprint_names.index(self.active_sprint['name']) if self.active_sprint else (len(self.sprint_names)-1 if self.year < self.now.year else 0))

        c1, c2 = st.columns([3, 2])
        with c1:
            with st.container(border=True):
                st.markdown("#### Edit Sprint")
                idx = self.sprint_names.index(selected_sprint_name)
                selected_sprint = self.sprints[idx]
                updated_sprint = {
                    "name": st.text_input("Sprint name", value = selected_sprint['name']),
                    "shortname": selected_sprint['shortname'],
                    "year": selected_sprint['year'],
                    "days": st.number_input("근무 일 수", value = selected_sprint['days']),
                    "availableSP": st.number_input("가용SP", value = selected_sprint['availableSP'])
                }
                if st.button("Save"):
                    num = self.db.update({'name': selected_sprint_name}, updated_sprint)
                    if num:
                        st.success("DB update successful")
                        selected_sprint_name = ""
                        updated_sprint = {}

        self.db.close()
        # print collab url of sprints
        self.collabs = {
            "2024": "http://collab.lge.com/main/pages/viewpage.action?pageId=2049915732",
            "2025": "http://collab.lge.com/main/pages/viewpage.action?pageId=2577787724",
            "2026": "http://collab.lge.com/main/pages/viewpage.action?pageId=3004510523"
        }
        st.write("{year}.Sprint.Collab".format(year=str(self.year)), self.collabs[str(self.year)])

    # 오늘 날짜로 active sprint를 찾음
    def findActiveSprint(self):
        now = dt.now()
        today = dt.now().strftime('%Y/%m/%d')
        for date in self.sprints:
            date_str = date['name']
            date_str = str(date_str).split("(")[1].split(")")[0]
            from_str = str(self.year)+"/"+date_str.split("-")[0]
            to_str = str(self.year)+"/"+date_str.split("-")[1]
            from_date = dt.strptime(from_str, '%Y/%m/%d')
            to_date = dt.strptime(to_str, '%Y/%m/%d')
            if from_date>to_date:
                from_str = str(self.year-1)+"/"+date_str.split("-")[0]
                from_date = dt.strptime(from_str, '%Y/%m/%d')
            
            if now > from_date and now < to_date:
                return date
        return None

    def getStartEndDateStr(self, sprint):
        sprint_name = sprint['name']
        date_str = str(sprint_name).split("(")[1].split(")")[0]
        from_str = str(self.year)+"/"+date_str.split("-")[0]
        to_str = str(self.year)+"/"+date_str.split("-")[1]
        from_date = dt.strptime(from_str, '%Y/%m/%d')
        to_date = dt.strptime(to_str, '%Y/%m/%d')
        if from_date>to_date:
            from_str = str(self.year-1)+"/"+date_str.split("-")[0]
            from_date = dt.strptime(from_str, '%Y/%m/%d')
        
        return from_date.strftime('%Y-%m-%d'), to_date.strftime('%Y-%m-%d')
        
        

sprint_setting = SprintSetting()
sprint_setting.renderPage()
