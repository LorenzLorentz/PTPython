import streamlit as st
import pandas as pd
from api import api_client

st.set_page_config(page_title="所有提交", page_icon="📝")

if not st.session_state.get("logged_in"):
    st.warning("请先在主页登录！")
    st.stop()

api_session = st.session_state.api_session
st.title("📝 代码提交记录")

# """加载提交"""
st.session_state.submission_list = api_client.get_submissions(api_session, st.session_state.user_id)
submissions = st.session_state.submission_list

if submissions is not None:
    st.header("提交列表")
    df_problems = pd.DataFrame(submissions)
    if not df_problems.empty and all(col in df_problems.columns for col in ['submission_id', 'status', 'score', 'counts']):
        st.dataframe(df_problems[['submission_id', 'status', 'score', 'counts']], use_container_width=True)
    else:
        st.warning("数据格式不正确")
        st.write(submissions)
        st.rerun()
else:
    st.error("加载题目列表失败")
    st.stop()