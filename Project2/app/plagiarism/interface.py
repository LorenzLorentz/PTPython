import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
import json

from app.plagiarism.get_report import get_report
from app.plagiarism.build_pdg import PDGBuilder
from app.db.database import SessionLocal
from app.db.models import SubmissionModel, PlagiarismTaskModel

def build(submission_id:int):
    """构建PDG"""
    db = SessionLocal()
    db_submission = db.get(SubmissionModel, submission_id)
    builder = PDGBuilder(db_submission.code)
    pdg = builder.build()
    db_submission.pdg = pdg
    db.commit()

def _calc_single(pdg_self:dict, pdg_other:dict, submission_id:int) -> tuple[int, int, dict]:
    """计算两个程序的PDG的相似度"""
    report = get_report(pdg_self, pdg_other)
    report = json.loads(report)
    return submission_id, report.get("sim_scores").get("sim_score"), report

def _collect(task_id:int):
    """发起相似度计算任务, 处理结果"""

    # 获取同题目提交
    db = SessionLocal()
    db_task = db.get(PlagiarismTaskModel, task_id)
    db_submission = db.get(SubmissionModel, db_task.submission_id)
    pdg_self = db_submission.pdg

    submissions = db.query(SubmissionModel).filter(SubmissionModel._problem_id==db_task._problem_id, SubmissionModel.language_id==2).all()

    if len(submissions) <= 1:
        return

    # 发起相似度计算任务
    results = []
    with ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(
                _calc_single,
                pdg_self,
                submission.pdg,
                submission.id,
            ): submission for submission in submissions
        }
        
        for future in as_completed(futures):
            results.append(future.result())
    
    # 处理结果, 计算final_report(查重报告), sim_list(相似度最高的5个的相似度)和sim_submission_id_list(相似度最高的5个题目)
    max_sim = 0.0
    final_report = None
    sim_list = []
    sim_submission_id_list = []
    
    for submission_id, sim, report in results:
        sim_list.append(sim)
        sim_submission_id_list.append(submission_id)
        
        if sim > max_sim:
            max_sim = sim
            final_report = report

    combined = list(zip(sim_list, sim_submission_id_list))
    combined.sort(reverse=True, key=lambda x: x[0])
    top_k = combined[:5]
    top_sim_list = [sim for sim, _ in top_k]
    top_sim_submission_id_list = [submission_id for _, submission_id in top_k]
    
    db_task.sim_abstract = final_report
    db_task.result = (max_sim >= db_task.threshold)
    db_task.sim_list = top_sim_list
    db_task.sim_submission_id_list = top_sim_submission_id_list
    
    db.commit()

def eval(task_id:int):
    """启动查重"""
    process = multiprocessing.Process(target=_collect, args=(task_id,))
    process.start()