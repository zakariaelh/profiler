import requests
import os
import subprocess
import shutil
import venv
import sys
import stat
import profiler_runner
import secret

def get_pr_info(owner, repo, pr_number):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {"Authorization": f"Bearer {secret.token}"}
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

def checkout_changes(sandbox_name, pr_info):
    head_ref = pr_info["head"]["ref"]  # Get the head branch from the PR info
    subprocess.run(["git", "checkout", head_ref], cwd=sandbox_name)

def create_venv(venv_path):
    venv.create(venv_path, with_pip=True)

def clone_pr_to_sandbox(owner, repo, pr_number, sandbox_name):
    pr_info = get_pr_info(owner, repo, pr_number)
    create_sandbox(sandbox_name)
    clone_repo(owner, repo, sandbox_name)
    fetch_pr(sandbox_name, pr_info, pr_number)
    checkout_changes(sandbox_name, pr_info)
    venv_name = 'venv'
    venv_path = f"{sandbox_name}/{venv_name}"
    create_venv(venv_path)

    # Shit set from the sandbox.
    pip_path = venv_path + "/bin/pip"  # Linux/macOS
    python_path = venv_path + "/bin/python"
    if sys.platform == "win32":
        pip_path = ".\/" + venv_path + "/Scripts/pip.exe"
        python_path = ".\/" + venv_path + "/Scripts/python.exe"
    requirements_path = f"{sandbox_name}/requirements.txt"

    # Shit needing to be built from our prod.
    file_paths_to_profile = "sandbox/profile_computer/experimental/cookie_test.py,sandbox/profile_computer/experimental/grundy_test.py"
    entry_point = "sandbox/profile_computer/experimental/main_test.py"

    process = subprocess.Popen([pip_path, "install", "-r", requirements_path])
    process.wait()
    prf = profiler_runner.get_latency_profile(file_paths_to_profile, entry_point, sandbox_name)
    print(prf)

owner = 'zakariaelh'
repo = 'profiler'
sandbox_name = 'sandbox'
pr_number = 1

clone_pr_to_sandbox(owner, repo, pr_number, sandbox_name)