from fastapi import APIRouter, HTTPException
from app.tasks.code_review_tasks import analyze_pr, analyze_format_data
from app.schema import AnalyzePRRequest
from celery.result import AsyncResult
from redis import Redis
import json

redis_client = Redis(host="localhost", port=6379, db=0)

router = APIRouter()

@router.post("/analyze-pr")
async def analyze_pr_endpoint(request: AnalyzePRRequest):
    repo_url = request.repo_url
    pr_number = request.pr_number
    github_token = request.github_token
    task = analyze_pr.apply_async(args=[repo_url, pr_number, github_token])
    return {"task_id": task.id}

@router.get("/status/{task_id}")
async def task_status(task_id: str):
    task = AsyncResult(task_id)
    data = redis_client.get(f"pr_analysis:{task_id}")

    response = {
        "task_id": task.id,
        "status": task.status,
        "data": data
    }
    res = analyze_format_data.delay(response)
    return {"task_id": task.id, "status": task.status if res else "PENDING"}

@router.get("/results/{task_id}")
async def task_results(task_id: str):
    task = AsyncResult(task_id)
    if task.status == "SUCCESS":
        return {"task_id": task.id, "status": task.status, "results": task.result}
    else:
        raise HTTPException(status_code=404, detail="Task not completed yet")
