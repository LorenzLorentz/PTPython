import docker
import os
import shutil
import time
from typing import List, Dict, Any
from celery import group, chain
from requests.exceptions import ReadTimeout

from app.judger.celery_app import celery_app
from app.db.database import SessionLocal
from app.db.models import SubmissionModel, StatusCategory, TestCaseResultModel
from app.schemas.language import LanguageBase
from app.schemas.problem import Case

client = docker.from_env()

DOCKER_IMAGE = {
    "cpp": "gcc:latest", 
    "python": "python:3.10-slim"
}

WORKDIR_BASE = "/tmp/" 
os.makedirs(WORKDIR_BASE, exist_ok=True)

STATUS_PRECEDENCE = {
    StatusCategory.AC: 0,
    StatusCategory.WA: 1,
    StatusCategory.RE: 2,
    StatusCategory.TL: 3,
    StatusCategory.MLE: 4,
    StatusCategory.CE: 5,
    StatusCategory.JUDGING: 6,
    StatusCategory.COMPILING: 7,
    StatusCategory.PENDING: 8,
    StatusCategory.UNK: 9,
}

@celery_app.task(name="tasks.eval", bind=True)
def eval(self, submission_id:int):
    db = SessionLocal()
    db_submission = db.query(SubmissionModel).filter(SubmissionModel.id == submission_id).first()

    if not db_submission:
        return

    db_submission.status = StatusCategory.COMPILING
    db.commit()

    work_dir = os.path.join(WORKDIR_BASE, str(submission_id))
    os.makedirs(work_dir, exist_ok=True)

    try:
        code_path = os.path.join(work_dir, "main" + db_submission.language.file_ext)
        with open(code_path, "w") as f:
            f.write(db_submission.code)
        
        if db_submission.language.compile_cmd:
            compile_command = db_submission.language.compile_cmd
            
            try:
                client.containers.run(
                    image=DOCKER_IMAGE.get(db_submission.language.name),
                    command=compile_command,
                    volumes={work_dir: {'bind': '/app', 'mode': 'rw'}},
                    working_dir='/app',
                    network_disabled=True,
                    user='nobody',
                    auto_remove=True,
                    mem_limit=f"{db_submission.problem.memory_limit * 2}m"
                )

                if not os.path.exists(os.path.join(work_dir, db_submission.language.exe_name)):
                    error(submission_id, StatusCategory.CE, work_dir, error_message="Compiler did not produce an executable.")
                    return

            except docker.errors.ContainerError as e:
                error_message = e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
                error(submission_id, StatusCategory.CE, work_dir, error_message=error_message)
                return

        db_submission.status = StatusCategory.JUDGING
        db.commit()
        
        run_tasks_group = group(
            run_task.s(
                id=i,
                case_id=case.id,
                work_dir=work_dir,
                language_dict=db_submission.language.__dict__,
                testcase_dict=case.__dict__,
                time_limit=db_submission.problem.time_limit,
                memory_limit=db_submission.problem.memory_limit
            ) for i, case in enumerate(db_submission.problem.testcases)
        )

        workflow = chain(run_tasks_group, collect_results_task.s(submission_id, work_dir))
        workflow.apply_async()

    except Exception as e:
        error(submission_id, StatusCategory.UNK, work_dir, error_message=str(e))
    finally:
        db.close()

@celery_app.task(name="tasks.run_task")
def run_task(id:int, case_id:int, work_dir:str, language_dict:dict, testcase_dict:dict, time_limit:float, memory_limit:int) -> Dict[str, Any]:
    language = LanguageBase(**language_dict)
    testcase = Case(**testcase_dict)
    
    input_path = os.path.join(work_dir, f"{id}.in")
    with open(input_path, "w") as f:
        f.write(testcase.input)

    run_command = f"sh -c '{language.run_cmd} < {id}.in'"

    container = None
    try:
        start_time = time.monotonic()
        container = client.containers.run(
            image=DOCKER_IMAGE.get(language.name, "ubuntu:latest"),
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
        time_used = time.monotonic() - start_time

        status_code = result_info.get('StatusCode', -1)
        stdout = container.logs(stdout=True, stderr=False).decode('utf-8', errors='ignore')
        stderr = container.logs(stdout=False, stderr=True).decode('utf-8', errors='ignore')
        memory_used = container.stats(stream=False).get("memory_stats", {}).get("max_usage", 0) / (1024*1024)

        result_status = StatusCategory.AC
        if time_used > time_limit:
            result_status = StatusCategory.TLE
        elif memory_used > memory_limit or status_code == 137:
            result_status = StatusCategory.MLE
        elif status_code != 0:
            result_status = StatusCategory.RE
        elif stdout.rstrip() != testcase.output.rstrip():
            result_status = StatusCategory.WA

        return {
            "id": id,
            "result": result_status,
            "time": time_used,
            "memory": memory_used,
            "case": testcase_dict,
            "output": stdout,
            "err_msg": stderr,
            "case_id": case_id,
        }
    except ReadTimeout:
        return {
            "id": id,
            "result": StatusCategory.TLE,
            "time": time_limit,
            "memory": 0,
            "case": testcase_dict,
            "output": "",
            "err_msg": "",
            "case_id": case_id,
        }
    except Exception as e:
        return {
            "id": id,
            "result": StatusCategory.TLE,
            "time": time_limit,
            "memory": 0,
            "case": testcase_dict,
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

    for test_case_result in test_case_results:
        max_time = max(max_time, test_case_result.get("time", 0))
        max_memory = max(max_memory, test_case_result.get("memory", 0))
        result = test_case_result["result"]

        if result == StatusCategory.AC:
            counts += 1
        
        if STATUS_PRECEDENCE.get(result, -1) > STATUS_PRECEDENCE.get(final_status, -1):
            final_status = result

    db = SessionLocal()
    # db_submission = db.query(SubmissionModel).get(submission_id)
    db_submission = db.query(SubmissionModel).filter(SubmissionModel.id == submission_id).first()

    db_submission.status = final_status
    db_submission.time = max_time
    db_submission.memory = max_memory
    db_submission.counts = counts*db_submission.score
    
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
                id=i,
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