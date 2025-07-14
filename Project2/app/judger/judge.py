import docker
import os
import shutil
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, Any
from requests.exceptions import ReadTimeout

from app.db.database import SessionLocal
from app.db.models import SubmissionModel, StatusCategory, SubmissionStatusCategory, TestCaseResultModel, LanguageModel, ProblemModel

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

def _run_single(
    test_case_result_id:int, case_id:int, work_dir:str, run_cmd:str, language_name:str,
    test_case_input:str, test_case_output:str, time_limit:float, memory_limit:int,
    judge_mode:str, spj:str
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
                # TBD!
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

def _prepare(submission_id: int):
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
            db_submission.status = SubmissionStatusCategory.COMPILING
            db.commit()
            try:
                client = docker.from_env(timeout=10)
                client.containers.run(
                    image=DOCKER_IMAGE.get(db_language.name),
                    command=db_language.compile_cmd,
                    volumes={work_dir: {'bind': '/app', 'mode': 'rw'}},
                    working_dir='/app',
                    network_disabled=True,
                    user='nobody',
                    auto_remove=True,
                    mem_limit=f"{memory_limit * 2}m"
                )
                if not os.path.exists(os.path.join(work_dir, "main")):
                    _error(submission_id, StatusCategory.CE, work_dir, "Compiler did not produce an executable.")
                    return
            except docker.errors.ContainerError as e:
                error_message = e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
                _error(submission_id, StatusCategory.CE, work_dir, err_msg=error_message)
                return

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
                    spj=db_problem.spj
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
        
        db_submission.status = SubmissionStatusCategory.SUCCESS if final_status_category == StatusCategory.AC else SubmissionStatusCategory.ERROR
        db_submission.time = max_time
        db_submission.memory = max_memory
        db_submission.score = total_score

        print([res for res in test_case_results])
        print(max_time, max_memory, final_status_category, total_score, db_submission.counts)
        
        db_submission.test_case_results = [
            TestCaseResultModel(submission_id=submission_id, **result) for result in test_case_results
        ]
        db.commit()

        _db_submission = db.query(SubmissionModel).filter(SubmissionModel.id==submission_id).first()
        with open("error.log", "a") as f:
            print("!!!", max_time, max_memory, final_status_category, total_score, db_submission.counts, file=f)
            print("123", _db_submission.score, _db_submission.counts, file=f)

    except Exception as e:
        _error(submission_id, StatusCategory.UNK, work_dir, err_msg=f"Main orchestrator failed: {str(e)}")
    finally:
        db.close()
        # if os.path.exists(work_dir):
        #     shutil.rmtree(work_dir)

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
                    case_id=case.id
                ) for i, case in enumerate(db_submission.problem.testcases)
            ]
            db.commit()
    finally:
        db.close()
        # if os.path.exists(work_dir):
        #     shutil.rmtree(work_dir)

def eval(submission_id: int):
    process = multiprocessing.Process(target=_prepare, args=(submission_id,))
    process.start()

if __name__ == "__main__":
    _prepare(1)