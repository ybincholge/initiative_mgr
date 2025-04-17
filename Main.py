import streamlit as st 

st.set_page_config(layout="wide")
st.logo("logo.png", size = 'large')

p1 = st.Page("pages/1 Initiatives.py", title = "Initiatives")
p2 = st.Page("pages/2 Sprint Planning.py", title = "Sprint Planning")
p3 = st.Page("pages/3 Sprint Review.py", title = "Sprint Review")
# p4 = st.Page("pages/5 Account Setting.py", title = "Account Setting")
#p4 = st.Page("pages/6 Organization.py", title = "Organization")

pg = st.navigation([p1, p2, p3 ])

pg.run()


st.title("Main")
# ID 입력 필드
user_id = st.text_input("ID", value=st.session_state.get('user_id', ''))

# Password 입력 필드 (mask 처리)
password = st.text_input("Password", type="password", value=st.session_state.get('password', ''))

# Role 선택 드롭다운
role_options = ["실장", "팀장", "파트장", "개발자"]
role = st.selectbox("Role", role_options, index=role_options.index(st.session_state.get('role', '개발자')))

# Save button
login_button = st.button("Log in")

# If the save button is clicked
if login_button:
    # Store the values in session state
    st.session_state["user_id"] = user_id
    st.session_state["password"] = password
    st.session_state["role"] = role
    # st.success("Login saved!")
