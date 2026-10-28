from fastapi import FastAPI,HTTPException
from problems import PROBLEMS
from pydantic import BaseModel,Field
from uuid import uuid4
from test_solver import run_experiment
app=FastAPI(title="Prompt Arena")
@app.get("/problems")
def get_problems():
    return[
        {
            "id":problem["id"],
            "title":problem["title"],
            "statement":problem["statement"].strip()
        }
        for problem in PROBLEMS.values()
    ]

@app.get("/problems/{problem_id}")
def get_problems(problem_id:str):
    problem=PROBLEMS.get(problem_id)
    if problem is None:
        raise HTTPException(
            status_code=404,
            detail="problem_found"
        )
    return {
        "id":problem["id"],
        "title":problem["title"],
        "statement":problem["statement"].strip(),
        "test_cases":problem["test_cases"]
    }

class ExperimentRequest(BaseModel):
    problem_id:str
    prompt:str=Field(min_lenght=1,max_length=10000)

@app.post("experiments")
def create_experiments(request:ExperimentRequest):
    problem=PROBLEMS.get(request.problem_id)
    if problem is None:
        raise HTTPException(
            status_code=404,
            detail="Problem does not found"
        )
    experiment_id = str(uuid4())

    return {
        "experiment_id": experiment_id,
        "problem_id": problem["id"],
        "problem_title": problem["title"],
        "prompt": request.prompt,
        "status": "pending"}
@app.post("/experiments")
def create_experiment(request: ExperimentRequest):
    problem = PROBLEMS.get(request.problem_id)

    if problem is None:
        raise HTTPException(
            status_code=404,
            detail="Problem not found"
        )

    if not request.prompt.strip():
        raise HTTPException(
            status_code=422,
            detail="Prompt cannot be empty"
        )

    result = run_experiment(
        problem=problem,
        prompt=request.prompt.strip()
    )

    return result
