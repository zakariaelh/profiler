import requests
import os
import subprocess
import shutil
import venv
import sys
import stat
import profiler_runner
from codechanger import get_pr_files, generate_name
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

def get_pr_info(owner, repo, pr_number):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def create_sandbox(sandbox_name):
    def remove_readonly(func, path, excinfo):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    if os.path.exists(sandbox_name):
        shutil.rmtree(sandbox_name, onerror=remove_readonly)

    os.mkdir(sandbox_name)
    print(f"Sandbox directory '{sandbox_name}' created successfully.")

def clone_repo(owner, repo, sandbox_name):
    subprocess.run(["git", "clone", f"https://github.com/{owner}/{repo}", sandbox_name])

def fetch_pr(sandbox_name, pr_info, pr_number):
    head_ref = pr_info["head"]["ref"]
    subprocess.run(["git", "fetch", "origin", f'pull/{pr_number}/head:{head_ref}'], cwd=sandbox_name)

def checkout_changes(sandbox_name, branch_name):
    subprocess.run(["git", "checkout", branch_name], cwd=sandbox_name)

def create_venv(venv_path):
    venv.create(venv_path, with_pip=True)

def clone_pr_to_sandbox(owner, repo, pr_number, branch_name=None):
    sandbox_name = generate_name(base_name="sandbox")

    create_sandbox(sandbox_name)
    clone_repo(owner, repo, sandbox_name)

    if not branch_name: 
        pr_info = get_pr_info(owner, repo, pr_number)
        fetch_pr(sandbox_name, pr_info, pr_number)
        branch_name = pr_info["head"]["ref"]  # Get the head branch from the PR info
    
    checkout_changes(sandbox_name, branch_name)
        
    venv_name = 'venv'
    venv_path = f"{sandbox_name}/{venv_name}"
    create_venv(venv_path)

    # Shit set from the sandbox.
    pip_path = venv_path + "/bin/pip"  # Linux/macOS
    
    if sys.platform == "win32":
        pip_path = ".\/" + venv_path + "/Scripts/pip.exe"
        python_path = ".\/" + venv_path + "/Scripts/python.exe"
    
    requirements_path = f"{sandbox_name}/requirements.txt"

    pr_files = get_pr_files(owner=owner, repo=repo, pr_number=pr_number)
    # Shit needing to be built from our prod.
    file_paths_to_profile = ",".join([f"{sandbox_name}/{file['filename']}" for file in pr_files])
    entry_point = "profile_computer/experimental/main_test.py"

    process = subprocess.Popen([pip_path, "install", "-r", requirements_path])
    process.wait()
    prf = profiler_runner.get_latency_profile(file_paths_to_profile, entry_point, sandbox_name)

    return prf 


if __name__ == "__main__":
    owner = 'zakariaelh'
    repo = 'profiler'
    sandbox_name = 'sandbox'
    pr_number = 1

    clone_pr_to_sandbox(owner, repo, pr_number)