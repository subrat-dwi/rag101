from fastapi import FastAPI, Query
from client.rq_client import queue
from queues.worker import process_query


app = FastAPI()

@app.get("/")
def root():
    return {"status": "Server is running"}

@app.post("/chat")
def chat(query: str = Query(..., description="The user's query to the chatbot")):
    job = queue.enqueue(process_query, query)

    return {
        "status": "Query has been received and is being processed",
        "job-id": job.id
        }

@app.get("/result")
def get_result(job_id: str = Query(..., description="The ID of the job to retrieve the result for")):
    job = queue.fetch_job(job_id)

    if job is None:
        return {"status": "Job not found"}

    if job.is_finished:
        return {
            "status": "Job completed",
            "result": job.result.choices[0].message.content
        }
    elif job.is_failed:
        return {"status": "Job failed"}
    else:
        return {"status": "Job is still processing"} 