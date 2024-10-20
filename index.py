from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import multiprocessing
from codechanger import generate_code_change, add_comment, generate_pull_request

app = FastAPI()

class ProfileRequest(BaseModel):
    repo: str
    owner: str
    pr_number: int

class ProfileResponse(BaseModel):
    profile_results: Dict[str, float]

def approve_latency_change(before_pr, with_pr, suggested_change):
    return {"is_approved": True}

@app.post("/get-profile", status_code=200)
async def get_profile(request: ProfileRequest):
    try:
        # Start the main process without waiting for results
        multiprocessing.Process(target=main, args=(request.repo, request.owner, request.pr_number)).start()
        return {"message": "Profiler process started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start profiler process: {str(e)}")

def get_latency_profile(owner, repo, pr_number, remote_branch, return_dict=None, key=None):
    if not pr_number:
        tmp =  "50ms"
    else:
        tmp = "100ms"
    if return_dict is not None and key:
        return_dict[key] = tmp 
    return tmp 

def main(repo: str, owner: str, pr_number: int):
    print(f"Received request for repo: {repo}, owner: {owner}, PR: {pr_number}")
    
    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    p1 = multiprocessing.Process(target=get_latency_profile, args=(owner, repo, None, return_dict, 'before'))
    p2 = multiprocessing.Process(target=get_latency_profile, args=(owner, repo, pr_number, return_dict, 'after'))

    # start processes 
    p1.start()
    p2.start()

    p1.join()
    p2.join()

    # convert return to dict 
    return_dict = dict(return_dict)
    
    # Generate code changes based on the latency results
    remote_branch = generate_code_change(owner, repo, pr_number, return_dict)

    # get latency profile after code changes 
    res = get_latency_profile(owner, repo, branch_name=remote_branch, return_dict={})

    res_approval = approve_latency_change(
        before_pr=return_dict.get('before', {}), 
        with_pr=return_dict.get('after', {}), 
        suggested_change=res)
    
    if res_approval['is_approved']:
        pr_url, _ = generate_pull_request(
            branch_name=remote_branch,
            owner=owner,
            repo=repo
        )
        add_comment(owner, repo, pr_number, pr_url, res_approval)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090)
