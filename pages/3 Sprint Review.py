import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="Initiative Manager", layout="wide")

# 로고 이미지 경로
LOGO_PATH = "logo.png"  # 로고 이미지 파일 경로를 설정하세요.

# 왼쪽 사이드바 구성
st.sidebar.image(LOGO_PATH, use_column_width=True)  # 로고 이미지 표시
st.sidebar.title("Menu")
st.sidebar.write("Select a page from the menu above.")