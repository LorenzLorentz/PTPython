import streamlit as st
from frontend import api_client

st.set_page_config(page_title="Online Judge", page_icon="⚖️")

"""session state初始化"""
if "api_session" not in st.session_state:
    st.session_state.api_session = None
if "username" not in st.session_state:
    st.session_state.username = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

"""退出登录"""
def handle_logout():
    st.session_state.api_session = None
    st.session_state.username = None
    st.session_state.logged_in = False
    st.success("您已成功登出!")
    # st.experimental_rerun()

"""页面渲染"""
st.title("Online Judge 系统")

# 如果用户已登录
if st.session_state.logged_in:
    st.subheader(f"你好, {st.session_state.username}!")
    st.info("你可以通过左侧的导航栏访问题目列表")
    if st.button("登出"):
        handle_logout()

# 如果用户未登录
else:
    st.subheader("请先登录")
    with st.form("login_form"):
        username = st.text_input("用户名", key="login_username")
        password = st.text_input("密码", type="password", key="login_password")
        submitted = st.form_submit_button("登录")

        if submitted:
            if not username or not password:
                st.warning("请输入用户名和密码.")
            else:
                session_obj = api_client.login(username, password)
                
                if session_obj:
                    st.session_state.api_session = session_obj
                    st.session_state.username = username
                    st.session_state.logged_in = True
                    # st.experimental_rerun()