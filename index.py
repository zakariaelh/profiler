from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import multiprocessing
from codechanger import generate_code_change, add_comment, generate_pull_request, get_pr_information
from repo_fetcher import clone_pr_to_sandbox
from llm import ChangeApprover

app = FastAPI()

class ProfileRequest(BaseModel):
    repo: str
    owner: str
    pr_number: int

class ProfileResponse(BaseModel):
    profile_results: Dict[str, float]

def approve_latency_change(before_results, after_results):
    res = ChangeApprover().get_response(
        before_results=before_results,
        after_results=after_results
    )
    return res 

@app.get("/")
def hi():
    return "Hi, welcome to profiler."

@app.post("/get-profile", status_code=200)
async def get_profile(request: ProfileRequest):
    print(request)
    try:
        # Start the main process without waiting for results
        multiprocessing.Process(target=main, args=(request.repo.split('/')[1], request.owner, request.pr_number)).start()
        return {"message": "Profiler process started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start profiler process: {str(e)}")

def get_latency_profile(owner, repo, pr_number, branch_name=None, return_dict=None, key=None):

    res = clone_pr_to_sandbox(owner=owner, repo=repo, pr_number=pr_number, branch_name=branch_name)
    
    return_dict[key] = res
    return res 

def main(repo: str, owner: str, pr_number: int):
    print(f"Received request for repo: {repo}, owner: {owner}, PR: {pr_number}")

    pr_info = get_pr_information(owner, repo, pr_number)
    base_hash = pr_info['base']['sha']
    
    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    p1 = multiprocessing.Process(target=get_latency_profile, args=(owner, repo), kwargs={'pr_number': pr_number, 'branch_name': base_hash, 'return_dict': return_dict, 'key': 'before'})
    p2 = multiprocessing.Process(target=get_latency_profile, args=(owner, repo), kwargs={'pr_number': pr_number, 'return_dict': return_dict, 'key': 'after'})

    # start processes 
    p1.start()
    p2.start()

    p1.join()
    p2.join()

    # convert return to dict 
    return_dict = dict(return_dict)
    # Generate code changes and get approval, up to 3 times or until approved
    for _ in range(3):
        try: 

            remote_branch, pr_title, pr_description = generate_code_change(owner, repo, pr_number, return_dict)

            # get latency profile after code changes 
            latency_res_after_llm = get_latency_profile(owner, repo, pr_number=pr_number, branch_name=remote_branch, return_dict={})

            res_approval = approve_latency_change(
                before_results=return_dict.get('after', {}), 
                after_results=latency_res_after_llm)

            if res_approval.is_approved:
                break

        except Exception as e:
            print(e)

    # If we've exited the loop, either we've got approval or we've run out of attempts
    
    if res_approval.is_approved:
        pr_url, _ = generate_pull_request(
            branch_name=remote_branch,
            owner=owner,
            repo=repo,
            title=pr_title,
            description=pr_description
        )
        add_comment(owner, repo, pr_number, pr_url, res_approval.approval_message)
    else:
        print('Changes were not approved')
        print(res_approval.approval_message)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090)
