import streamlit as st
import pandas as pd
from utils import api_client
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="题目与提交", page_icon="📝")

if not st.session_state.get("logged_in"):
    st.warning("请先在主页登录！")
    st.stop()

api_session = st.session_state.api_session
st.title("📝 题目列表与代码提交")

"""加载题目"""
if 'problems_list' not in st.session_state:
    with st.spinner("正在加载题目列表..."):
        st.session_state.problems_list = api_client.get_problems(api_session)

problems = st.session_state.problems_list

if problems is not None:
    st.header("题目列表")
    df_problems = pd.DataFrame(problems)
    if not df_problems.empty and all(col in df_problems.columns for col in ['id', 'title']):
        st.dataframe(df_problems[['id', 'title']], use_container_width=True)
    else:
        st.warning("数据格式不正确")
        st.write(problems)
        st.stop()
else:
    st.error("加载题目列表失败")
    st.stop()


"""提交代码"""
st.header("提交代码")
with st.form("submission_form"):
    problem_options = {f"{p['id']}: {p['title']}": p['id'] for p in problems}
    selected_problem_display = st.selectbox("选择题目", options=list(problem_options.keys()))
    problem_id = problem_options[selected_problem_display]

    languages = api_client.get_languages(api_session)
    if languages:
        selected_lang_name = st.selectbox("选择语言", options=languages)
    else:
        st.error("无法加载语言列表。")
        st.stop()

    code = st.text_area("输入你的代码", height=400, key="code_input")
    submit_button = st.form_submit_button("提交")

"""轮询"""
POLL_INTERVAL_SECONDS = 2
POLL_LIMIT = 10

if submit_button:
    if not code.strip():
        st.warning("代码不能为空!")
    else:
        with st.spinner("正在提交代码..."):
            submission_id = api_client.submit_code(
                session=api_session,
                problem_id=problem_id,
                language_name=selected_lang_name,
                code=code
            )

        if submission_id:
            st.balloons()
            st.session_state.is_polling = True
            st.session_state.submission_id = submission_id
            st.session_state.poll_count = 0
            st.session_state.final_result = None
            st.rerun()
        else:
            st.error("提交失败，未能获取到 Submission ID。")

if st.session_state.get("is_polling"):
    
    submission_id = st.session_state.submission_id
    st.info(f"提交 ID 为: {submission_id}. 评测中...")

    # a. 检查是否超时
    if st.session_state.poll_count >= POLL_LIMIT:
        st.warning("评测超时")
        st.session_state.is_polling = False
        st.rerun()

    # b. 如果没超时且没拿到结果，则设置自动刷新器
    if st.session_state.is_polling:
        st_autorefresh(interval=POLL_INTERVAL_SECONDS * 1000, limit=POLL_LIMIT + 1, key="submission_refresher")

    # c. 执行一次查询
    status_placeholder = st.empty()
    status_placeholder.write(f"查询中 (第 {st.session_state.poll_count + 1}/{POLL_LIMIT} 次)...")
    
    result = api_client.get_submission_result(api_session, submission_id)
    st.session_state.poll_count += 1 

    if result and result.get("status") != "pending":
        st.success("评测完成!")
        # 将最终结果存入 session_state
        st.session_state.final_result = {
            "status": result.get("status"),
            "score": result.get("score"),
            "counts": result.get("counts")
        }
        st.session_state.is_polling = False
        status_placeholder.empty()
        st.rerun()

# 4. 显示最终结果
if st.session_state.get("final_result"):
    st.subheader("最新评测结果")
    st.json(st.session_state.final_result)