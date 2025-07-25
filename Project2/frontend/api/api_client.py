import requests
import streamlit as st

BASE_URL = "http://127.0.0.1:8001"

"""登录认证"""
def get_auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}

"""用户登录与身份管理"""
def login(username:str, password:str) -> tuple[requests.Session, int]:
    session = requests.Session()
    try:
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"username":username, "password":password},
        )

        print("------ DEBUG LOGIN RESPONSE ------")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Response Text: {response.text}")
        print("----------------------------------")

        if response.status_code == 200:
            st.success("登录成功!")
            return session, response.json().get("data").get("user_id")
        else:
            st.error(f"登录失败: {response.json().get('detail', '未知错误')}")
            return None, None
    except requests.exceptions.RequestException as e:
        st.error(f"请求错误: {e}")
        return None, None

"""题目展示"""
def get_problems(session:requests.Session):
    if not session:
        return None

    try:
        response = session.get(f"{BASE_URL}/api/problems/")
        
        print("------ DEBUG PROBLEM RESPONSE ------")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Response Text: {response.text}")
        print("----------------------------------")

        if response.status_code == 200:
            return response.json().get("data")
        else:
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"获取题目列表时出错: {e}")
        return None

"""代码提交与结果查询"""
def get_languages(session:requests.Session):
    try:
        response = session.get(f"{BASE_URL}/api/languages/")
        if response.status_code == 200:
            return response.json().get("data").get("name")
        else:
            return ["python", "cpp"]
    except requests.exceptions.RequestException:
        return ["python", "cpp"]

def submit_code(session:requests.Session, problem_id:str, language_name:str, code:str):
    payload = {
        "problem_id": problem_id,
        "language": language_name,
        "code": code
    }

    try:
        response = session.post(
            f"{BASE_URL}/api/submissions/",
            json=payload,
        )

        print("------ DEBUG SUBMISSION RESPONSE ------")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Response Text: {response.text}")
        print("----------------------------------")

        if response.status_code == 200:
            st.success("代码提交成功!")
            return response.json().get("data").get("submission_id")
        else:
            st.error(f"提交失败: {response.json().get('msg')}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"提交代码时出错: {e}")
        return None

def get_submission_result(session:requests.Session, submission_id:int):
    try:
        response = session.get(
            f"{BASE_URL}/api/submissions/{submission_id}",
        )
        
        print("------ DEBUG RESULT RESPONSE ------")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Response Text: {response.text}")
        print("----------------------------------")

        if response.status_code == 200:
            return response.json().get("data")
        else:
            st.error(f"查询失败: {response.json().get('msg')}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"查询提交 {submission_id} 时出错: {e}")
        return None
    
"""所有结果"""
def get_submissions(session:requests.Session, user_id:int):
    try:
        response = session.get(
            f"{BASE_URL}/api/submissions/?user_id={user_id}",
        )

        print("------ DEBUG SUBMISSION LIST RESPONSE ------")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Response Text: {response.text}")
        print("----------------------------------")

        if response.status_code == 200:
            return response.json().get("data").get("submissions")
        else:
            st.error(f"查询失败: {response.json().get('msg')}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"查询用户 {user_id} 的提交时出错: {e}")
        return None