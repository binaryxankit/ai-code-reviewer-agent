from celery import Celery
from app.models.pr_analyzer import analyze_pr_code
from app.models.pr_analyzer import format_data
from redis import Redis
import json
import os

redis_client = Redis(host="localhost", port=6379, db=0)
celery = Celery("code_review_tasks", broker=os.getenv("REDIS_URL"), backend=os.getenv("REDIS_URL"))

@celery.task(bind=True)
def analyze_pr(self, repo_url: str, pr_number: int, github_token: str = None):
    try:
        result = analyze_pr_code(repo_url, pr_number, github_token)
        redis_client.set(f"pr_analysis:{self.request.id}", json.dumps(result))
        return result
    except Exception as e:
        print(f"Error ==============: {e}")
        raise self.retry(exc=e)


@celery.task(bind=True)
def analyze_format_data(self, formatData):
    try:
        result = format_data(formatData)
        update = redis_client.set(f"pr_analysis:{self.request.id}", json.dumps(result))
        return update
    except Exception as e:
        print(f"Error ==============: {e}")
        raise self.retry(exc=e)
