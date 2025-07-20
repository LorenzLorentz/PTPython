import requests
import uuid
import time
import json

# --- 配置 ---
BASE_URL = "http://127.0.0.1:8001/api"
ADMIN_USER = "admin"
ADMIN_PW = "admin" # 默认管理员密码，根据实际情况修改
POLL_INTERVAL = 2 # 轮询评测结果的间隔时间（秒）
MAX_POLL_ATTEMPTS = 15 # 最大轮询次数

# --- 辅助函数 ---

def pretty_print_json(data, title=""):
    """格式化打印JSON"""
    if title:
        print(f"--- {title} ---")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("\n")

def setup_session(username=None, password=None):
    """创建一个新的requests session并登录"""
    session = requests.Session()
    if username and password:
        login_data = {"username": username, "password": password}
        try:
            r = session.post(f"{BASE_URL}/auth/login", data=login_data)
            r.raise_for_status()
            if r.json().get("code") != 200:
                raise Exception(f"登录失败: {r.json().get('msg')}")
            # print(f"用户 '{username}' 登录成功.")
        except requests.exceptions.RequestException as e:
            print(f"无法连接到API或登录失败: {e}")
            print("请确保FastAPI服务正在 http://127.0.0.1:8000 运行.")
            exit(1)
    return session

def poll_for_result(session, submission_id):
    """轮询直到获取最终评测结果"""
    print(f"正在等待评测结果 (Submission ID: {submission_id})...")
    for attempt in range(MAX_POLL_ATTEMPTS):
        try:
            r = session.get(f"{BASE_URL}/submissions/{submission_id}")
            r.raise_for_status()
            data = r.json()
            status = data.get("data", {}).get("status")
            if status not in ["pending", "judging", "compiling"]:
                print("评测完成.")
                return data
            time.sleep(POLL_INTERVAL)
        except requests.exceptions.RequestException as e:
            print(f"轮询时出错: {e}")
            return None
    print("轮询超时.")
    return None

# --- 主逻辑 ---

def main():
    # 1. 初始化管理员会话并创建题目
    admin_session = setup_session(ADMIN_USER, ADMIN_PW)
    
    problem_id = "report_demo_" + uuid.uuid4().hex[:6]
    problem_data = {
        "id": problem_id,
        "title": "两数之和 (报告演示)",
        "description": "输入两个整数，输出它们的和。",
        "input_description": "输入为一行，包含两个整数。",
        "output_description": "输出这两个整数的和。",
        "samples": [{"input": "1 2", "output": "3"}],
        "testcases": [
            {"input": "1 2", "output": "3"},
            {"input": "-10 20", "output": "10"}
        ],
        "constraints": "|a|,|b| <= 10^9",
        "time_limit": 2.0, # 设置为2秒以防CI/CD环境过慢
        "memory_limit": 128,
        "difficulty": "入门"
    }
    print(f"正在创建题目: {problem_id}")
    admin_session.post(f"{BASE_URL}/problems/", json=problem_data)

    # 2. 创建并登录测试用户
    test_user = "user_" + uuid.uuid4().hex[:8]
    test_pw = "pw_" + uuid.uuid4().hex[:8]
    admin_session.post(f"{BASE_URL}/users/", json={"username": test_user, "password": test_pw})
    user_session = setup_session(test_user, test_pw)
    
    # 3. 提交AC, WA, TLE代码并获取结果
    
    # --- 场景一: Accepted ---
    ac_code = "a, b = map(int, input().split())\nprint(a + b)"
    r_ac = user_session.post(f"{BASE_URL}/submissions/", json={
        "problem_id": problem_id, "language": "python", "code": ac_code
    })
    ac_submission_id = r_ac.json()["data"]["submission_id"]
    ac_result = poll_for_result(user_session, ac_submission_id)
    if ac_result:
        pretty_print_json(ac_result, "评测结果: Accepted (AC)")

    # --- 场景二: Wrong Answer ---
    wa_code = "a, b = map(int, input().split())\nprint(a - b)" # 错误逻辑
    r_wa = user_session.post(f"{BASE_URL}/submissions/", json={
        "problem_id": problem_id, "language": "python", "code": wa_code
    })
    wa_submission_id = r_wa.json()["data"]["submission_id"]
    wa_result = poll_for_result(user_session, wa_submission_id)
    if wa_result:
        pretty_print_json(wa_result, "评测结果: Wrong Answer (WA)")

    # --- 场景三: Time Limit Exceeded ---
    tle_code = "while True:\n  pass"
    r_tle = user_session.post(f"{BASE_URL}/submissions/", json={
        "problem_id": problem_id, "language": "python", "code": tle_code
    })
    tle_submission_id = r_tle.json()["data"]["submission_id"]
    tle_result = poll_for_result(user_session, tle_submission_id)
    if tle_result:
        pretty_print_json(tle_result, "评测结果: Time Limit Exceeded (TLE)")

    # 4. 获取题目列表和提交列表的JSON
    
    # --- 场景四: 获取题目列表 ---
    r_problems = admin_session.get(f"{BASE_URL}/problems/")
    pretty_print_json(r_problems.json(), "题目列表 (`GET /api/problems/`)")

    # --- 场景五: 获取用户提交记录 ---
    user_info_r = admin_session.get(f"{BASE_URL}/users/?username={test_user}")
    user_id = user_info_r.json()['data']['items'][0]['id']

    r_submissions = admin_session.get(f"{BASE_URL}/submissions/?user_id={user_id}")
    pretty_print_json(r_submissions.json(), f"用户提交记录 (`GET /api/submissions/?user_id={user_id}`)")


if __name__ == "__main__":
    main()
