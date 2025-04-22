import streamlit as st


# ID 입력 필드
user_id = st.text_input("ID", value=st.session_state.get('user_id', ''))

# Password 입력 필드 (mask 처리)
password = st.text_input("Password", type="password", value=st.session_state.get('password', ''))

# Role 선택 드롭다운
role_options = ["실장", "팀장", "파트장", "개발자"]
role = st.selectbox("Role", role_options, index=role_options.index(st.session_state.get('role', '개발자')))

# Save button
save_button = st.button("Save")

# If the save button is clicked
if save_button:
    # Store the values in session state
    st.session_state["user_id"] = user_id
    st.session_state["password"] = password
    st.session_state["role"] = role
    st.success("Settings saved!")