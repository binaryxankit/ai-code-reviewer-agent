import requests
from dotenv import load_dotenv
import os
from requests.exceptions import RequestException
import google.generativeai as genai
from app.config import summary, FinalData
import json

load_dotenv()

def fetch_pr_diff(repo_url: str, pr_number: int, github_token: str = None):
    """
    Fetches the PR diff from GitHub.

    Args:
        repo_url (str): The GitHub repository URL.
        pr_number (int): The pull request number.
        github_token (str, optional): GitHub token for authentication.

    Returns:
        str or None: The diff content, or None if an error occurs.
    """
    headers = {"Authorization": f"token {github_token}"} if github_token else {}
    repo_path = repo_url.replace("https://github.com/", "")
    api_url = f"https://api.github.com/repos/{repo_path}/pulls/{pr_number}"

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        diff_url = response.json().get("diff_url")
        if diff_url:
            diff_response = requests.get(diff_url, headers=headers)
            diff_response.raise_for_status()
            return diff_response.text  # Return the diff content
        else:
            print("Error: Diff URL not found in the PR metadata.")
            return None
    except RequestException as e:
        print(f"Error fetching PR diff: {e}")
        return None


def analyze_pr_diff(pr_diff: str):
    """
    Analyzes the PR diff using Bard for issues, bugs, style violations, and best practices.

    Args:
        pr_diff (str): The pull request diff content.

    Returns:
        dict: Analysis results or an error message.
    """
    bard_api_key = os.getenv("BARD_API_KEY")
    if not bard_api_key:
        print("Error: BARD_API_KEY not found in environment variables.")
        return {"error": "BARD_API_KEY missing"}

    # Configure GenAI with Bard API
    genai.configure(api_key=bard_api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Generate content using Bard
    try:
        response = model.generate_content(f"""
        Analyze the following PR diff for issues, bugs, style violations, and best practices.
        Provide suggestions for improvement. Format your response as JSON with each file, issues (type, line, description, suggestion), and a summary object:
        {pr_diff} like {summary}
        """)
        cleaned_response = response.text.replace('json', '').replace('```', '')
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Error analyzing PR diff: {e}")
        return {"error": str(e)}


def analyze_pr_code(repo_url: str, pr_number: int, github_token: str = None):
    """
    Main function to fetch the PR diff and analyze it.

    Args:
        repo_url (str): The GitHub repository URL.
        pr_number (int): The pull request number.
        github_token (str, optional): GitHub token for authentication.

    Returns:
        dict: The combined results of the analysis or an error message.
    """
    # Step 1: Fetch PR Diff
    pr_diff = fetch_pr_diff(repo_url, pr_number, github_token)
    if not pr_diff:
        return {"error": "Failed to fetch PR diff"}

    # Step 2: Analyze the PR Diff
    analysis_results = analyze_pr_diff(pr_diff)
    return analysis_results



def format_data(formatData):
    bard_api_key = os.getenv("BARD_API_KEY")
    if not bard_api_key:
        print("Error: BARD_API_KEY not found in environment variables.")
        return {"files": []}
    
    genai.configure(api_key=bard_api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    try:
        response = model.generate_content(f"summarise and format the following data in better. This is the response of the files {formatData} now modify it to the structure of the Data like this {FinalData}")
        return response.text.replace('json', '').replace('```', '')
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {e}
