import docker
import os
import shutil
import time
from typing import List, Dict, Any
from celery import group, chain, current_app
from celery.signals import worker_process_init
from requests.exceptions import ReadTimeout

from app.judger.celery_app import celery_app
from app.db.database import SessionLocal
from app.db.models import SubmissionModel, StatusCategory, TestCaseResultModel, LanguageModel, ProblemModel

@worker_process_init.connect(weak=False)
def init_docker_client(**kwargs):
    current_app.docker_client = docker.from_env(timeout=10)

DOCKER_IMAGE = {
    "cpp": "gcc-judge:latest", 
    "python": "python-judge:latest"
}

WORKDIR_BASE = os.path.expanduser("~/tmp/")
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

@celery_app.task(name="tasks.eval", bind=True)
def eval(self, submission_id:int):
    client = current_app.docker_client
    db = SessionLocal()
    db_submission = db.query(SubmissionModel).filter(SubmissionModel.id == submission_id).first()
    db_language = db.query(LanguageModel).filter(LanguageModel.id == db_submission.language_id).first()
    db_problem = db.query(ProblemModel).filter(ProblemModel.id == db_submission._problem_id).first()

    time_limit = db_problem.time_limit
    memory_limit = db_problem.memory_limit
    if time_limit is None:
        time_limit = db_language.time_limit
    if memory_limit is None:
        memory_limit = db_language.memory_limit

    if not db_submission:
        return

    db_submission.counts = 10*len(db_problem.testcases)
    db_submission.status = StatusCategory.COMPILING
    db.commit()

    work_dir = os.path.join(WORKDIR_BASE, str(submission_id))
    os.makedirs(work_dir, exist_ok=True)

    try:
        code_path = os.path.join(work_dir, "main" + db_language.file_ext or "")
        with open(code_path, "w") as f:
            f.write(db_submission.code)
        
        if db_language.compile_cmd:
            compile_command = db_language.compile_cmd
            try:
                client.containers.run(
                    image=DOCKER_IMAGE.get(db_language.name),
                    command=compile_command,
                    volumes={work_dir: {'bind': '/app', 'mode': 'rw'}},
                    working_dir='/app',
                    network_disabled=True,
                    user='nobody',
                    auto_remove=True,
                    mem_limit=f"{memory_limit*2}m"
                )

                if not os.path.exists(os.path.join(work_dir, "main" + db_language.file_ext or "")):
                    error(submission_id, StatusCategory.CE, work_dir, err_msg="Compiler did not produce an executable.")
                    return

            except docker.errors.ContainerError as e:
                error_message = e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
                error(submission_id, StatusCategory.CE, work_dir, err_msg=error_message)
                return
        
        db_submission.status = StatusCategory.JUDGING
        db.commit()

        run_tasks_group = group(
            run_task.s(
                test_case_result_id=i+1,
                case_id=case.id,
                work_dir=work_dir,
                run_cmd=db_language.run_cmd,
                language_name=db_language.name,
                test_case_input=case.input,
                test_case_output=case.output,
                time_limit=time_limit,
                memory_limit=memory_limit
            ) for i, case in enumerate(db_problem.testcases)
        )

        workflow = chain(run_tasks_group, collect_results_task.s(submission_id, work_dir))
        workflow.apply_async()
    except Exception as e:
        error(submission_id, StatusCategory.UNK, work_dir, err_msg=str(e))
    finally:
        db.close()

@celery_app.task(name="tasks.run_task")
def run_task(test_case_result_id:int, case_id:int, work_dir:str, run_cmd:str, language_name:str, test_case_input:str, test_case_output:str, time_limit:float, memory_limit:int) -> Dict[str, Any]:
    client = current_app.docker_client
    input_path = os.path.join(work_dir, f"{test_case_result_id}.in")
    with open(input_path, "w") as f:
        f.write(test_case_input)

    run_command = f"sh -c \"/usr/bin/time -f 'TIME:%U %S' {run_cmd} < {test_case_result_id}.in\""

    container = None
    try:
        start_time = time.monotonic()

        container = client.containers.run(
            image=DOCKER_IMAGE.get(language_name, "ubuntu:latest"),
            command=run_command,
            volumes={work_dir: {'bind': '/app', 'mode': 'ro'}},
            working_dir='/app',
            mem_limit=f"{memory_limit}m",
            memswap_limit=f"{memory_limit}m",
            network_disabled=True,
            user='nobody',
            detach=True
        )

        result_info = container.wait(timeout=time_limit * 1.2)

        status_code = result_info.get('StatusCode', -1)
        stdout = container.logs(stdout=True, stderr=False).decode('utf-8', errors='ignore')
        stderr = container.logs(stdout=False, stderr=True).decode('utf-8', errors='ignore')
        memory_used = container.stats(stream=False).get("memory_stats", {}).get("max_usage", 0) / (1024*1024)

        time_parts = []
        user_stderr = []
        for line in stderr.splitlines():
            if line.startswith("TIME:"):
                parts = line.split(":")[-1].strip().split()
                time_parts.extend(parts)
            else:
                user_stderr.append(line)

        if time_parts:
            time_used = sum(float(t) for t in time_parts)
            err_msg = "\n".join(user_stderr)
        else:
            time_used = time.monotonic() - start_time
            err_msg = stderr

        result_status = "AC"
        if time_used > time_limit:
            result_status = "TLE"
        elif memory_used > memory_limit or status_code == 137:
            result_status = "MLE"
        elif status_code != 0:
            result_status = "RE"
        elif stdout.rstrip() != test_case_output.rstrip():
            result_status = "WA"

        return {
            "test_case_result_id": test_case_result_id,
            "result": result_status,
            "time": time_used,
            "memory": memory_used,
            "output": stdout,
            "err_msg": stderr,
            "case_id": case_id,
        }
    except ReadTimeout:
        return {
            "test_case_result_id": test_case_result_id,
            "result": "TLE",
            "time": time_limit,
            "memory": 0,
            "output": "",
            "err_msg": "Wait Time Out",
            "case_id": case_id,
        }
    except Exception as e:
        return {
            "test_case_result_id": test_case_result_id,
            "result": "TLE",
            "time": time_limit,
            "memory": 0,
            "output": "",
            "err_msg": str(e),
            "case_id": case_id,
        }
    finally:
        if container:
            try:
                container.remove(force=True)
            except docker.errors.NotFound:
                pass

@celery_app.task(name="tasks.collect_results_task")
def collect_results_task(test_case_results:List[Dict[str, Any]], submission_id:int, work_dir:str):
    final_status = StatusCategory.AC
    max_time = 0.0
    max_memory = 0
    counts = 0

    if not isinstance(test_case_results, list):
        test_case_results = [test_case_results]
    
    for test_case_result in test_case_results:
        with open("error.log", "a") as f:
            print(test_case_result, file=f)

        max_time = max(max_time, test_case_result.get("time", 0))
        max_memory = max(max_memory, test_case_result.get("memory", 0))
        result = STATUS_DICT.get(test_case_result["result"], StatusCategory.UNK)

        if result == StatusCategory.AC:
            counts += 1
        
        if STATUS_PRECEDENCE.get(result, -1) > STATUS_PRECEDENCE.get(result, -1):
            final_status = result

    db = SessionLocal()
    # db_submission = db.query(SubmissionModel).get(submission_id)
    db_submission = db.query(SubmissionModel).filter(SubmissionModel.id == submission_id).first()

    db_submission.status = final_status
    db_submission.time = max_time
    db_submission.memory = max_memory
    db_submission.score = 10*counts

    with open("error.log", "a") as f:
        print(max_time, max_memory, result, counts, db_submission.counts, db_submission.score, file=f)
    
    db_submission.test_case_results = [
        TestCaseResultModel(submission_id=submission_id, **test_case_result) for test_case_result in test_case_results
    ]

    db.commit()
    db.close()

    if os.path.exists(work_dir):
        shutil.rmtree(work_dir)

def error(submission_id:int, result:str, work_dir:str, err_msg:str=""):
    db = SessionLocal()
    # db_submission = db.query(SubmissionModel).get(submission_id)
    db_submission = db.query(SubmissionModel).filter(SubmissionModel.id == submission_id).first()

    if db_submission:
        db_submission.status = result
        
        db_submission.test_case_results = [
            TestCaseResultModel(
                submission_id=submission_id,
                test_case_result_id=i+1,
                result=result,
                time=0.0,
                memory=0,
                output="",
                err_msg=err_msg,
                case_id=case.id
            ) for i, case in enumerate(db_submission.problem.testcases)
        ]
        
        db.commit()
    
    db.close()

    if os.path.exists(work_dir):
        shutil.rmtree(work_dir)