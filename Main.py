import json
from account_util import *
import streamlit as st
import time

account = get_account()

if account is not None:
    user_id = account['user_id']
    password = account['password']
    role = account['role']
else:
    user_id = ''
    password = ''
    role = '개발자'

if not user_id or not password:
    # ID 입력 필드
    st.markdown('## Login')
    st.markdown('###')
    
    user_id = st.text_input('### :male-office-worker: Enter your AD account', key=user_id, value=user_id, max_chars=20)

    # Password 입력 필드 (mask 처리)
    password = st.text_input("### :key: Password", placeholder="비밀번호는 서버에 저장되지 않고 로컬 브라우저에 암호화하여 저장합니다.", type="password", key=password, value=password, max_chars=20)

    # Role 선택 드롭다운
    role_options = ["실장", "팀장", "파트장", "개발자"]
    role = st.selectbox(":hammer_and_wrench: Role", role_options, index=role_options.index(role))

    # Save button
    check_button = st.button("Check")
    # If the save button is clicked
    if check_button:
        try:
            jira = login(user_id, password)
        except:
            st.badge("Login authentication failure")
        else:        
            st.session_state['account'] = set_account(st, {'user_id': user_id, "password": password, "role":role})
            time.sleep(5)
            st.success("Login successful")
        
        
