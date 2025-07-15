import docker
import os
import shutil
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, Any, Optional
from requests.exceptions import ReadTimeout

from app.db.database import SessionLocal
from app.db.models import (
    SubmissionModel, StatusCategory, SubmissionStatusCategory, TestCaseResultModel, LanguageModel, ProblemModel, UserModel
)

"""黑名单、白名单校验"""
def check_cmd_available(cmd:Optional[str]) -> bool:
    # 白名单
    whitelist_prefixes = [
        "gcc", "g++", "python", "python3", "timeout", "/usr/bin/time"
    ]

    # 黑名单
    blacklist_keywords = [
        "rm", "shutdown", "reboot", "mkfs", "dd", "kill", "init", "telnet",
        "ftp", "nc", "ncat", "wget", "curl", "scp", "chmod", "chown", ">", ">>",
        "echo", "cat", "nano", "vi", ";", "&&", "|", "`", "$(", "docker", "mount",
        "umount"
    ]
    
    if cmd is None:
        return True

    cmd = cmd.strip()

    # 黑名单检测
    for keyword in blacklist_keywords:
        if keyword in cmd:
            return False

    # 白名单检测
    for prefix in whitelist_prefixes:
        if cmd.startswith(prefix):
            return True

    return False

"""参数设置"""
client = docker.from_env(timeout=10)

DOCKER_IMAGE = {
    "cpp": "gcc-judge:latest",
    "python": "python-judge:latest"
}

WORKDIR_BASE = os.path.expanduser("~/tmp/pa2-oj-2024010860")
os.makedirs(WORKDIR_BASE, exist_ok=True)

STATUS_PRECEDENCE = {
    StatusCategory.AC: 0,
    StatusCategory.WA: 1,
    StatusCategory.RE: 2,
    StatusCategory.TLE: 3,
    StatusCategory.MLE: 4,
    StatusCategory.CE: 5,
    StatusCategory.JUDGING: 6,
    StatusCategory.COMPILING: 7,
    StatusCategory.PENDING: 8,
    StatusCategory.UNK: 9,
}

STATUS_DICT = {
    "AC": StatusCategory.AC,
    "WA": StatusCategory.WA,
    "RE": StatusCategory.RE,
    "TLE": StatusCategory.TLE,
    "MLE": StatusCategory.MLE,
    "CE": StatusCategory.CE,
    "JUDGING": StatusCategory.JUDGING,
    "COMPILING": StatusCategory.COMPILING,
    "PENDING": StatusCategory.PENDING,
    "UNK": StatusCategory.UNK,
}

def _prepare_spj(work_dir:str,problem:ProblemModel, memory_limit:int) -> Optional[str]:
    spj_lang = problem.spj_language
    spj_lang_name = spj_lang.name
    spj_src_filename = f"spj{spj_lang.file_ext or ''}"
    
    spj_code_path = os.path.join(work_dir, spj_src_filename)
    with open(spj_code_path, "w") as f:
        f.write(problem.spj_code)

    if spj_lang.compile_cmd:
        spj_compile_cmd = spj_lang.compile_cmd.replace("main.cpp", spj_src_filename).replace("main", "spj")
        try:
            client.containers.run(
                image=DOCKER_IMAGE[spj_lang_name],
                command=spj_compile_cmd,
                volumes={work_dir: {'bind': '/app', 'mode': 'rw'}},
                working_dir='/app',
                network_disabled=True,
                user='root',
                mem_limit=f"{memory_limit * 2}m",
                auto_remove=True,
            )
            if not os.path.exists(os.path.join(work_dir, "spj")):
                raise RuntimeError("SPJ compilation did not produce an executable.")
            return "./spj"
        except docker.errors.ContainerError as e:
            err_msg = e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
            raise RuntimeError(f"SPJ Compilation Error: {err_msg}")
    else:
        spj_run_cmd = spj_lang.run_cmd.replace("main.py", spj_src_filename)
        return spj_run_cmd

def _run_spj(
    work_dir:str, spj_run_cmd:str, spj_language_name:str,
    input_file:str, user_output_file:str, answer_file:str
) -> str:
    container = None
    try:
        spj_command = f"{spj_run_cmd} {input_file} {user_output_file} {answer_file}"
        container = client.containers.run(
            image=DOCKER_IMAGE[spj_language_name],
            command=spj_command,
            volumes={work_dir: {'bind': '/app', 'mode': 'rw'}},
            working_dir='/app',
            network_disabled=True,
            user='nobody',
            detach=True
        )
        
        result_info = container.wait(timeout=2)
        status_code = result_info.get('StatusCode', -1)
        spj_out = container.logs(stdout=True, stderr=False).decode('utf-8', errors='ignore')
        
        if status_code == 0:
            return spj_out
        else:
            return None
    except Exception as e:
        return None
    finally:
        if container:
            try:
                container.remove(force=True)
            except:
                pass

def _run_single(
    test_case_result_id:int, case_id:int, 
    work_dir:str, 
    run_cmd:str, language_name:str,
    test_case_input:str, test_case_output:str, time_limit:float, memory_limit:int,
    judge_mode:str, spj_run_cmd:str, spj_language_name:str,
) -> Dict[str, Any]:
    """运行测例"""
    input_filename = f"{test_case_result_id}.in"
    input_path = os.path.join(work_dir, input_filename)
    with open(input_path, "w") as f:
        f.write(test_case_input)

    run_command = f"sh -c \"/usr/bin/time -f 'TIME:%U %S' {run_cmd} < {input_filename}\""
    
    container = None
    try:
        container = client.containers.run(
            image=DOCKER_IMAGE.get(language_name),
            command=run_command,
            volumes={work_dir: {'bind': '/app', 'mode': 'ro'}},
            working_dir='/app',
            mem_limit=f"{memory_limit}m",
            memswap_limit=f"{memory_limit}m",
            network_disabled=True,
            user='nobody',
            detach=True
        )

        result_info = container.wait(timeout=time_limit*1.2)
        status_code = result_info.get('StatusCode', -1)

        stdout = container.logs(stdout=True, stderr=False).decode('utf-8', errors='ignore')
        stderr = container.logs(stdout=False, stderr=True).decode('utf-8', errors='ignore')
        memory_used = container.stats(stream=False).get("memory_stats", {}).get("max_usage", 0) / (1024*1024)

        time_parts = []
        user_stderr = []
        for line in stderr.splitlines():
            if line.startswith("TIME:"):
                time_parts.extend(line.split(":")[-1].strip().split())
            else:
                user_stderr.append(line)

        time_used = sum(float(t) for t in time_parts)
        err_msg = "\n".join(user_stderr) if time_parts else stderr

        result_status = "AC"
        score = None
        if time_used > time_limit:
            result_status = "TLE"
        elif memory_used > memory_limit or status_code == 137:
            result_status = "MLE"
        elif status_code != 0:
            result_status = "RE"
        else:
            if judge_mode == "standard":
                if stdout.rstrip() != test_case_output.rstrip():
                    result_status = "WA"
            elif judge_mode == "strict":
                if stdout != test_case_output:
                    result_status = "WA"
            elif judge_mode == "spj":
                if spj_run_cmd and spj_language_name:
                    user_out_file = f"{test_case_result_id}.user.out"
                    ans_file = f"{test_case_result_id}.ans"
                    with open(os.path.join(work_dir, user_out_file), "w") as f: f.write(stdout)
                    with open(os.path.join(work_dir, ans_file), "w") as f: f.write(test_case_output)
                    
                    score = _run_spj(work_dir, spj_run_cmd, spj_language_name, input_filename, user_out_file, ans_file)
                    try:
                        if score == 10:
                            result_status = "AC"
                        elif 0 <= score <10:
                            result_status = "WA"
                        else:
                            result_status = "UNK"
                    except:
                        result_status = "UNK"
                else:
                    if stdout.rstrip() != test_case_output.rstrip():
                        result_status = "WA"

        return {
            "test_case_result_id": test_case_result_id, "result": result_status,
            "time": time_used, "memory": memory_used, "output": stdout,
            "err_msg": err_msg, "case_id": case_id, "score": score,
        }
    except ReadTimeout:
        return {
            "test_case_result_id": test_case_result_id, "result": "TLE",
            "time": time_limit, "memory": 0, "output": "", 
            "err_msg": "Container wait timed out.", "case_id": case_id, "score": 0
        }
    except Exception as e:
        return {
            "test_case_result_id": test_case_result_id, "result": "UNK",
            "time": 0, "memory": 0, "output": "",
            "err_msg": f"Runner Error: {str(e)}", "case_id": case_id, "score": 0
        }
    finally:
        if container:
            try:
                container.remove(force=True)
            except docker.errors.NotFound:
                pass

def _collect(submission_id:int):
    """获取信息, 编译程序"""
    work_dir = os.path.join(WORKDIR_BASE, str(submission_id))
    os.makedirs(work_dir, exist_ok=True)
    db = SessionLocal()

    try:
        db_submission = db.get(SubmissionModel, submission_id)
        if not db_submission:
            return

        db_language = db.get(LanguageModel, db_submission.language_id)
        db_problem = db.get(ProblemModel, db_submission._problem_id)

        time_limit = db_problem.time_limit or db_language.time_limit
        memory_limit = db_problem.memory_limit or db_language.memory_limit

        db_submission.counts = 10*len(db_problem.testcases)
        db_submission.status = SubmissionStatusCategory.PENDING
        db.commit()

        """编译"""
        code_path = os.path.join(work_dir, "main" + (db_language.file_ext or ""))
        with open(code_path, "w") as f:
            f.write(db_submission.code)

        if db_language.compile_cmd:
            try:
                client = docker.from_env(timeout=10)
                client.containers.run(
                    image=DOCKER_IMAGE.get(db_language.name),
                    command=db_language.compile_cmd,
                    volumes={work_dir: {'bind': '/app', 'mode': 'rw'}},
                    working_dir='/app',
                    network_disabled=True,
                    user='root',
                    mem_limit=f"{memory_limit * 2}m",
                    auto_remove=True,
                )

                if not os.path.exists(os.path.join(work_dir, "main")):
                    _error(submission_id, StatusCategory.CE, work_dir, "Compiler did not produce an executable.")
                    return
            except docker.errors.ContainerError as e:
                print(e)
                error_message = e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
                _error(submission_id, StatusCategory.CE, work_dir, err_msg=error_message)
                return

        if db_problem.judge_mode == 'spj':
            try:
                spj_run_cmd = _prepare_spj(work_dir, db_problem, memory_limit)
            except (ValueError, RuntimeError, docker.errors.DockerException) as e:
                _error(submission_id, StatusCategory.UNK, work_dir, f"System Error: SPJ setup failed. {e}")
                return
        else:
            spj_run_cmd = None

        db_submission.status = SubmissionStatusCategory.PENDING
        db.commit()
        
        test_case_results = []

        with ProcessPoolExecutor() as executor:
            futures = {
                executor.submit(
                    _run_single,
                    test_case_result_id=i + 1,
                    case_id=case.id,
                    work_dir=work_dir,
                    run_cmd=db_language.run_cmd,
                    language_name=db_language.name,
                    test_case_input=case.input,
                    test_case_output=case.output,
                    time_limit=time_limit,
                    memory_limit=memory_limit,
                    judge_mode=db_problem.judge_mode,
                    spj_run_cmd=spj_run_cmd,
                    spj_language_name=db_problem.spj_language_name,
                ): case for i, case in enumerate(db_problem.testcases)
            }
            
            for future in as_completed(futures):
                test_case_results.append(future.result())

        test_case_results.sort(key=lambda r: r['test_case_result_id'])
        
        final_status_category = StatusCategory.AC
        max_time = 0.0
        max_memory = 0.0
        total_score = 0

        for res in test_case_results:
            max_time = max(max_time, res.get("time", 0))
            max_memory = max(max_memory, res.get("memory", 0))
            
            current_res_category = STATUS_DICT.get(res["result"], StatusCategory.UNK)
            
            # Update final status based on precedence
            if STATUS_PRECEDENCE.get(current_res_category, 99) > STATUS_PRECEDENCE.get(final_status_category, 99):
                final_status_category = current_res_category
            
            score = res.pop("score", None)
            if score is not None:
                total_score += score
            elif current_res_category == StatusCategory.AC:
                total_score += 10
        
        db_submission.status = SubmissionStatusCategory.SUCCESS if (
            final_status_category == StatusCategory.AC
            or final_status_category == StatusCategory.WA
        ) else SubmissionStatusCategory.ERROR
        db_submission.time = max_time
        db_submission.memory = max_memory
        db_submission.score = total_score

        print([res for res in test_case_results])
        print(max_time, max_memory, final_status_category, total_score, db_submission.counts)
        
        if db_submission.status == SubmissionStatusCategory.SUCCESS:
            db_user = db.get(UserModel, db_submission.user_id)
            db_user.resolve_count += 1

        db_submission.test_case_results = [
            TestCaseResultModel(submission_id=submission_id, **result) for result in test_case_results
        ]
        db.commit()

    except Exception as e:
        _error(submission_id, StatusCategory.UNK, work_dir, err_msg=f"Main orchestrator failed: {str(e)}")
    finally:
        db.close()
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)

def _error(submission_id:int, result:StatusCategory, work_dir:str, err_msg:str=""):
    """更新错误状态"""
    db = SessionLocal()
    try:
        db_submission = db.get(SubmissionModel, submission_id)
        if db_submission:
            db_submission.status = SubmissionStatusCategory.ERROR
            db_submission.test_case_results = [
                TestCaseResultModel(
                    submission_id=submission_id,
                    test_case_result_id=i + 1,
                    result=result,
                    time=0.0,
                    memory=0,
                    output="",
                    err_msg=err_msg,
                    case_id=case.id,
                ) for i, case in enumerate(db_submission.problem.testcases)
            ]
            db.commit()
    finally:
        db.close()
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)

def eval(submission_id: int):
    process = multiprocessing.Process(target=_collect, args=(submission_id,))
    process.start()