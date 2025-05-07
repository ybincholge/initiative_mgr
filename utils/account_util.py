#import json
from jira.client import JIRA
#import jira.config
from st_local_storage import *
import streamlit as st
import base64  # string 데이터를 encode / decode 하기 위한 라이브러리
import rsa  # rsa 모듈을 이용해서 메세지를 암호화 할 것

class AccountUtil:
    def __init__(self):
        self.sls = StLocalStorage()
        self.account = {}
        # self.org_setting = orgsettings


    def chk_n_display_login(self): 
        account = self.get_account()
        # if not "logged_in" in st.session_state or not st.session_state['logged_in']:
        #     with st.spinner("Loading ... ⏳"):
        #         time.sleep(1)

        if account:
            self.account = account
            user_id = account['user_id']
            password = account['password']
            # role = account['role']
            try:
                jira = self.login(user_id, password)
            except:
                self.logout()
                return
            else:
                st.session_state.logged_in = True
                self.account["username"] = jira.user(jira.current_user()).displayName
                st.session_state['user_id'] = user_id
                st.session_state['account'] = self.account
                st.session_state['jira'] = jira
                return self.account

        else:
            user_id = ''
            password = ''
            # role = '개발자'

            # ID 입력 필드
            st.header('Account Setting')
            st.markdown("")
            
            col1, col2 = st.columns([2,3])
            with col1:
                with st.container(border=True):
                    user_id = st.text_input('### :male-office-worker: User ID', placeholder='JIRA 로그인을 위한 AD계정 아이디', max_chars=20)

                    # Password 입력 필드 (mask 처리)
                    password = st.text_input("### :key: Password", placeholder="비밀번호는 서버에 전송되지 않고 브라우저의 로컬스토리지에 암호화하여 저장합니다.", type="password", key=password, value=password, max_chars=20)

                    # role_options = ["실장", "팀장", "파트장", "개발자"]
                    # role = st.selectbox(":hammer_and_wrench: Initial View", role_options, index=role_options.index(role))

                    # Save button
                    save = st.button("Save")
                    # If the save button is clicked
                    if save:
                        try:
                            jira = self.login(user_id, password)
                        except:
                            st.badge("Login authentication failure. Please check again.", icon=":material/warning:", color = 'red')
                        else:
                            st.session_state.logged_in = True
                            username = jira.user(jira.current_user()).displayName
                            st.session_state['user_id'] = user_id
                            account = {'user_id': user_id, "password": password, 'username': username, "org": {"sil": [], "team": [], "part":[]}}
                            self.set_account(account)
                            st.success("Login successful")
                            st.session_state['account'] = account
                            st.session_state['jira'] = jira
                            return account


    def handle_logout(self):
        self.account = self.accUtil.logout()

    def login(self, user_id, password):
        options = {'server': 'http://hlm.lge.com/issue'}
        jira = JIRA(options, basic_auth=(user_id, password))
        return jira

    def logout(self):
        del st.session_state['account']
        del st.session_state['jira']
        # self.sls.set('account', {})
        self.sls.remove("account")
        print("yb set empty ojbect completed!!!")
        print("get account : "+str(self.sls.get("account")))
        return

    def get_account(self):
        account = self.sls.get("account")
        if account:
            pwd_byte = base64.b64decode(account['password'])
            private_key_bytes = open('private.pem', 'rb').read()
            private_key = rsa.PrivateKey.load_pkcs1(keyfile=private_key_bytes)
            account['password'] = rsa.decrypt(pwd_byte, private_key).decode('utf-8')
        return account

    def set_account(self, account):
        public_key_bytes = open('public.pem', 'rb').read() 
        public_key = rsa.PublicKey.load_pkcs1_openssl_pem(keyfile=public_key_bytes)
        # user_id_bytes = rsa.encrypt(acc["user_id"].encode('utf-8'), public_key)
        password_bytes = rsa.encrypt(account["password"].encode('utf-8'), public_key)
        # user_id_msg = base64.b64encode(user_id_bytes).decode('utf-8')
        password_msg = base64.b64encode(password_bytes).decode('utf-8')
        # role = acc['role']
        # account = {"user_id": user_id_msg, "password": password_msg, "role": role}
        account['password'] = password_msg
        self.sls.set('account', account)

    def login(self, jid, pwd):
        jira = JIRA(server='http://hlm.lge.com/issue', basic_auth=(jid, pwd))
        return jira


    def get_username_jira(self, acc_id):
        error = False
        try:
            jira = st.session_state['jira']
            username = jira.user(acc_id).displayName
        except:
            error = True

        if error:
            # try again
            try:
                account = self.account
                if account:
                    j = self.login(account['user_id'], account['password'])
                    username = j.user(acc_id).displayName
            except:
                return ""

        return username

