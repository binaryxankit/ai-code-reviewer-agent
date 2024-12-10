import requests
from dotenv import load_dotenv
import os
from requests.exceptions import RequestException
import google.generativeai as genai
from app.config import Data, FinalData

load_dotenv()

def fetch_files_from_github(repo_url, pr_number, github_token):
    headers = {"Authorization": f"token {github_token}"} if github_token else {}
    repo_path = repo_url.replace("https://github.com/", "")
    api_url = f"https://api.github.com/repos/{repo_path}/pulls/{pr_number}/files"

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        files_data = response.json()
        
        files = []
        for file in files_data:
            if file["status"] in ["added", "modified"]:
                raw_url = file["raw_url"]
                try:
                    file_content = requests.get(raw_url, headers=headers).text
                    files.append({"name": file["filename"], "content": file_content})
                except RequestException as e:
                    print(f"Error fetching file content from {raw_url}: {e}")
        return files

    except RequestException as e:
        print(f"Error fetching files from GitHub: {e}")
        return []  # Return empty list on error
    except (KeyError, ValueError) as e:
        print(f"Error parsing GitHub response: {e}, Response: {response.text}")
        return []


def analyze_pr_code(repo_url: str, pr_number: int, github_token: str = None):

    files = fetch_files_from_github(repo_url, pr_number, github_token)

    formatData = {
        "results": {
            "files": []
        },
        "summary": {
            "total_files": 0,
            "total_issues": 0,
            "critical_issues": 0
        }
    }


    bard_api_key = os.getenv("BARD_API_KEY")
    if not bard_api_key:
        print("Error: BARD_API_KEY not found in environment variables.")
        return {"files": []}
    
    genai.configure(api_key=bard_api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    for file in files:
        try:
            response = model.generate_content(f"Analyze the following code for potential issues, bugs or errors, Code Style, formatting issues, best practices and improvements. Each file with issues with type, line, description, suggestion and all this should be in array of objects and each object have name of the file and issues have the array of objects and each array of objects have type, line, description, suggestion and if there is multiple files then all files should be in array of objects and also there will be summary object which will have total files, total issues, critical issues in the last :\n{file['content']}")

            cleaned = response.text.replace('json', '').replace('```', '')  
            formatData["results"]["files"].append(cleaned)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            formatData["results"]["files"].append({"name": file['name'], "issues": f"Bard analysis failed: {e}"})

    finalData = model.generate_content(f"summarise and format the following data in better. This is the response of the files {formatData} now modify it to the structure of the Data like this {Data}")

    return finalData.text.replace('json', '').replace('```', '')


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
