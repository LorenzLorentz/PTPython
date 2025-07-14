import streamlit as st
import pandas as pd
from utils import api_client
import time

st.set_page_config(page_title="题目与提交", page_icon="📝")

if not st.session_state.get("logged_in"):
    st.warning("请先在主页登录！")
    st.stop()

api_session = st.session_state.api_session
st.title("📝 题目列表与代码提交")

with st.spinner("正在加载题目列表..."):
    problems = api_client.get_problems(api_session)

if problems is not None:
    st.header("题目列表")
    df_problems = pd.DataFrame(problems)
    if not df_problems.empty and all(col in df_problems.columns for col in ['id', 'title']):
        st.dataframe(df_problems[['id', 'title']], use_container_width=True)
    else:
        st.warning("题目数据格式不正确，无法显示列表。")
        st.write(problems)
        st.stop()
else:
    st.error("无法加载题目列表。请检查后端服务或你的登录状态。")
    st.stop()

st.header("提交代码")
with st.form("submission_form"):
    problem_options = {f"{p['id']}: {p['title']}": p['id'] for p in problems}
    selected_problem_display = st.selectbox("选择题目", options=list(problem_options.keys()))
    problem_id = problem_options[selected_problem_display]

    languages = api_client.get_languages(api_session)
    if languages:
        selected_lang_name = st.selectbox(
            "选择语言",
            options=languages # 直接使用返回的字符串列表
        )
    else:
        st.error("无法加载语言列表。")
        st.stop()

    code = st.text_area("输入你的代码", height=400, key="code_input")
    submit_button = st.form_submit_button("提交")

if submit_button:
    if not code.strip():
        st.warning("代码不能为空！")
    else:
        with st.spinner("正在提交代码..."):
            submission_id = api_client.submit_code(session=api_session, problem_id=problem_id, language_name=selected_lang_name, code=code)

        if submission_id:
            st.info(f"你的提交 ID 是: **{submission_id}**。系统正在评测中...")
            st.balloons()
            
            # 轮询逻辑保持不变
            status_placeholder = st.empty()
            result_placeholder = st.empty()
            for i in range(10):
                with status_placeholder.container():
                    details = api_client.get_submission_result(api_session, submission_id)
                    if details:
                        status = details.get("status", "未知状态")
                        st.write(f"查询中 ({i+1}/10)... 最新状态: **{status}**")
                        if status not in ["pending", "judging"]:
                            with result_placeholder:
                                st.success("评测完成！")
                                st.json(details)
                            break
                    time.sleep(2)
            else:
                 with result_placeholder:
                    st.warning("评测超时，请稍后在“我的提交”页面查看最终结果。")
