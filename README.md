# Code Review Agent

This project is a code review agent that analyzes pull requests in a GitHub repository. It uses FastAPI for the API, Celery for task management, LLM Bard API for code review, python-dotenv for environment variables, and Redis for caching.

## Technologies Used

- FastAPI
- Celery
- Redis
- Python
- GitHub API
- LLM Bard API (Gemini 1.5 Flash model)

## Purpose

The purpose of this project is to automate the code review process by analyzing pull requests and providing feedback so that developers can focus on writing code and improving their code quality faster.

## Project Structure

```plaintext
code-review-agent/
│
├── .env                     # Environment variables for configuration
├── .Readme.md               # Project documentation
├── app/                     # Main application directory
│   ├── requirements.txt     # List of dependencies
│   ├── main.py              # FastAPI application entry point
│   ├── tasks/               # Directory for Celery tasks
│   │   └── code_review_tasks.py  # Code review task definitions
│   └── ...                  # Other application files
└── ...                      # Other project files
```

## Setup Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/ThakurAnkitSingh/Code-Review-Agent-AI-Backend.git
   cd code-review-agent
   ```

2. **Create a Virtual Environment (Optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `./venv/Scripts/activate`
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r app/requirements.txt
   ```

4. **Configure Environment Variables:**
   - Create a `.env` file in the root directory (`code-review-agent/.env`) and add the necessary environment variables, such as:
     ```
     GITHUB_TOKEN=your_github_token
     REDIS_URL=redis://localhost:6379/0
     LLM_API_KEY=your_llm_api_key (for example: BARD_API_KEY)
     ```

5. **Start the Celery Worker:**
   ```bash
   celery -A app.tasks.code_review_tasks worker --pool=solo
   ```

6. **Start the FastAPI Server:**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

1. **Analyze Pull Request:**
   - **Endpoint:** `/analyze-pr`
   - **Method:** POST
   - **Request Body:**
     ```json
     {
         "repo_url": "https://github.com/username/repo",
         "pr_number": 123,
         "github_token": "your_github_token"
     }
     ```
   - **Response:**
     ```json
     {
         "task_id": "task_id"
     }
     ```

2. **Check Task Status:**
   - **Endpoint:** `/status/{task_id}`
   - **Method:** POST
   - **Request Body:**
     ```json
     {
         "task_id": "task_id"
     }
     ```
   - **Response:**
     ```json
     {
         "task_id": "task_id",
         "status": "status"
     }
     ```

3. **Get Task Results:**
   - **Endpoint:** `/results/{task_id}`
   - **Method:** POST
   - **Request Body:**
     ```json
     {
         "task_id": "task_id"
     }
     ```
   - **Response:**
     ```json
     {
         "task_id": "task_id",
         "status": "status",
         "data": {
             "files": [
                 {
                     "name": "main.py",
                     "issues": [
                         {
                             "type": "style",
                             "line": 15,
                             "description": "Line too long",
                             "suggestion": "Break line into multiple lines"
                         },
                         {
                             "type": "bug",
                             "line": 23,
                             "description": "Potential null pointer",
                             "suggestion": "Add null check"
                         }
                     ]
                 }
             ],
             "summary": {
                 "total_files": 1,
                 "total_issues": 2,
                 "critical_issues": 1
             }
         }
     }
     ```

## How to Start the Project

1. Install the required dependencies from `app/requirements.txt`.
2. Start the Celery worker with the command `celery -A app.tasks.code_review_tasks worker --pool=solo`.
3. Start the FastAPI server with the command `uvicorn app.main:app --reload`.
