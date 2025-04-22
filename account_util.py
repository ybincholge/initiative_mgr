#import json
from jira.client import JIRA
#import jira.config
from st_local_storage import *

import base64  # string 데이터를 encode / decode 하기 위한 라이브러리
import rsa  # rsa 모듈을 이용해서 메세지를 암호화 할 것
       

def get_account():
    sls = StLocalStorage()

    account = sls.get("account")
    if account is not None:
        pwd_byte = base64.b64decode(account['password'])
        private_key_bytes = open('private.pem', 'rb').read()
        private_key = rsa.PrivateKey.load_pkcs1(keyfile=private_key_bytes)
        account['password'] = rsa.decrypt(pwd_byte, private_key).decode('utf-8')
    return account
    # if account is None:
    #     return None
    # user_id_bytes = base64.b64decode(account['user_id'])
    # password_bytes = base64.b64decode(account['password'])
    # role = account['role']
    # private_key_bytes = open('private.pem', 'rb').read()
    # private_key = rsa.PrivateKey.load_pkcs1(keyfile=private_key_bytes)
    # user_id = rsa.decrypt(user_id_bytes, private_key).decode('utf-8')
    # password = rsa.decrypt(password_bytes, private_key).decode('utf-8')
    # role = account['role']
    # account = {'user_id': user_id, 'password': password, 'role': role}
    # return account

def set_account(st, account):
    sls = StLocalStorage()

    public_key_bytes = open('public.pem', 'rb').read() 
    public_key = rsa.PublicKey.load_pkcs1_openssl_pem(keyfile=public_key_bytes)
    # user_id_bytes = rsa.encrypt(acc["user_id"].encode('utf-8'), public_key)
    password_bytes = rsa.encrypt(account["password"].encode('utf-8'), public_key)
    # user_id_msg = base64.b64encode(user_id_bytes).decode('utf-8')
    password_msg = base64.b64encode(password_bytes).decode('utf-8')
    # role = acc['role']
    # account = {"user_id": user_id_msg, "password": password_msg, "role": role}
    account['password'] = password_msg
    sls.set('account', account)




def login(jid, pwd):
    jira = JIRA(server='http://hlm.lge.com/issue', basic_auth=(jid, pwd))
    return jira
