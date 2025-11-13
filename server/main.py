import os
import shutil
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
from celery import Celery

# FastAPI app
app = FastAPI(title="PDF/DOCX to Markdown Converter API")

# Celery configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery = Celery("markitdown_api", broker=REDIS_URL, backend=REDIS_URL)

# Storage directories
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/data/uploads")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/data/output")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.post("/convert")
async def upload_file(file: UploadFile):
    """
    Upload a PDF or DOCX file and enqueue a conversion task.
    """
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    task = celery.send_task("convert_to_markdown", args=[file_path])
    return {"task_id": task.id, "message": "File uploaded and conversion started."}


@app.get("/status/{task_id}")
def get_status(task_id: str):
    """
    Check the status of a conversion task.
    """
    task = celery.AsyncResult(task_id)
    return {"task_id": task_id, "status": task.status}


@app.get("/result/{task_id}")
def get_result(task_id: str):
    """
    Return the output Markdown file once the task is complete.
    """
    task = celery.AsyncResult(task_id)

    if task.state != "SUCCESS":
        raise HTTPException(status_code=404, detail=f"Task not ready or failed: {task.state}")

    result_path = task.result
    if not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="Converted file not found.")

    return FileResponse(result_path, media_type="text/markdown", filename=os.path.basename(result_path))


@app.get("/tasks")
def list_all_tasks():
    """
    Return a list of all known tasks with their current statuses.
    """
    tasks = load_tasks()
    result = []
    for t in tasks:
        task = celery.AsyncResult(t["task_id"])
        result.append({
            "task_id": t["task_id"],
            "filename": t["filename"],
            "status": task.status
        })
    return {"count": len(result), "tasks": result}