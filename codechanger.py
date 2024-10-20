import string
import requests
import random
from typing import List
from dotenv import load_dotenv
import os
import subprocess
from github import Github
import re
from tqdm import tqdm
from llm import CodeChangeGenerator, LineChangeFixer, CodeChange, Patch

load_dotenv()
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
github_client = Github(GITHUB_TOKEN)


def get_pr_information(owner: str, repo: str, pr_number: int) -> dict:
    repo = github_client.get_repo(f"{owner}/{repo}")
    pr = repo.get_pull(pr_number)
    print(f'fetching PR information for {pr_number}')
    return pr.raw_data


def get_file_content(file, owner, repo):
    filepath = file['filename']
    # GitHub API URL
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filepath}"

    # Set up the headers
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.raw"  # Ensures we get raw file content
    }

    # Make the GET request to fetch the file content
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch file content. Status code: {response.status_code} from {url}")

def add_line_numbers(content):
    lines = content.split('\n')
    numbered_lines = [f"<{i+1}>{line}" for i, line in enumerate(lines)]
    return '\n'.join(numbered_lines)

def remove_line_numbers(content):
    lines = content.split('\n')
    unnumbered_lines = [re.sub(r'<\d+>\s', '', line) for line in lines]
    return '\n'.join(unnumbered_lines)

def add_file_content_inplace(file, owner, repo) -> str:
    # get file content 
    file_content = get_file_content(file, owner, repo)

    # add line number to each line 
    numbered_content = add_line_numbers(file_content)

    # update file dict  
    file['content'] = numbered_content
    file['raw_content'] = file_content


def _get_pr_files(pull_request) -> List[dict]:
    return [i.raw_data for i in pull_request.get_files()]


def get_changes_from_llm(file, latency_profile):
    prompt = get_prompt(file, latency_profile=latency_profile)

    changes = send_prompt_to_llm(prompt)

    return changes 

def get_pull_requests(owner, repo):
    """
    Retrieves all pull requests for a given repository.
    
    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
    
    Returns:
        list: A list of PullRequest objects.
    """
    repository = github_client.get_repo(f"{owner}/{repo}")
    pull_requests = list(repository.get_pulls(state='open'))
    return pull_requests


def get_pr_files(owner: str, repo: str, pr_number: int):
    repo_obj = github_client.get_repo(f"{owner}/{repo}")
    pr = repo_obj.get_pull(pr_number)
    pr_files = _get_pr_files(pr)

    for file in pr_files:
        file['owner'] = owner
        file['repo'] = repo 
        # add content of the file 
        add_file_content_inplace(file, owner, repo)
    
    return pr_files
    
def update_file(file: dict, updated_content: str):
    # load file 
    local_file_path = file['local_file_path']
    
    # Write the updated content to the file
    with open(local_file_path, 'w') as f:
        f.write(updated_content)

    print(f'{file["filename"]} has been updated')

def apply_patch_to_file(patch: Patch, file: dict):
    if not patch.patch:
        print(f"Empty patch for {file['filename']}")
        return 
    # apply the patch to the file 
    lines = file['raw_content'].split('\n')
    # remove line numbers from the patch 
    tmp = remove_line_numbers(patch.patch)
    new_lines = tmp.split('\n')
    lines[patch.start:patch.end] = new_lines
    new_file_content = '\n'.join(lines)

    update_file(file, new_file_content)

def combine_close_changes(changes: List[CodeChange], max_distance: int = 10) -> List[List[CodeChange]]:
    if not changes:
        return []

    # Sort changes by start line
    sorted_changes = sorted(changes, key=lambda x: x.line_start)
    
    combined = []
    current_group = [sorted_changes[0]]

    for change in sorted_changes[1:]:
        if change.line_start - current_group[-1].line_end <= max_distance:
            current_group.append(change)
        else:
            combined.append(current_group)
            current_group = [change]

    # Add the last group
    combined.append(current_group)

    return combined

def remove_line_numbers(text: str) -> str:    
    return re.sub(r'<\d+>', '', text)

def generate_name(base_name):
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{base_name}-{random_suffix}"

def go_to_branch(owner, repo, pr_number):
    base_path = os.path.expanduser("~/Downloads")  # Use user's home directory
    full_directory = os.path.join(base_path, repo)

    if not os.path.exists(full_directory):
        print(f"Directory '{full_directory}' does not exist. Cloning repository...")
        clone_command = f"git clone https://github.com/{owner}/{repo}.git {full_directory}"
        try:
            subprocess.run(clone_command, shell=True, check=True)
            print(f"Successfully cloned repository to {full_directory}")
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repository: {e}")
            return False

    branch_name = generate_name(base_name='profiler')

    commands = [
        "git stash",
        "git checkout main",
        f"git fetch origin pull/{pr_number}/head:{branch_name}",
        f"git checkout {branch_name}"
    ]

    for command in commands:
        try:
            subprocess.run(command, shell=True, check=True, cwd=full_directory)
            print(f"Executed: {command}")
        except subprocess.CalledProcessError as e:
            print(f"Error executing '{command}': {e}")
            return False

    print(f"Successfully switched to branch for PR #{pr_number}")
    return full_directory, branch_name

def publish_branch(local_branch_name, directory):
    try:
        remote_branch = local_branch_name
        subprocess.run("git add .", shell=True, check=True, cwd=directory)
        subprocess.run('git commit -m "optimization by profiler"', shell=True, check=True, cwd=directory)
        subprocess.run(f"git push origin {local_branch_name}:{remote_branch}", shell=True, check=True, cwd=directory)
        print(f"Successfully published branch {local_branch_name}")
        return remote_branch
    except subprocess.CalledProcessError as e:
        print(f"Error publishing branch: {e}")
        raise

def generate_pull_request(branch_name: str, owner: str, repo: str, title=None, description=None):
    repository = github_client.get_repo(f"{owner}/{repo}")

    if not description:
        description = "This pull request contains optimizations generated by the profiler."

    # Create the pull request
    pr = repository.create_pull(
        title=f"Profiler AI Optimization: {title}",
        body=description,
        head=branch_name,
        base="main",
        draft=False
    )

    print(f"Successfully created PR #{pr.number} for branch {branch_name} in {owner}/{repo} \n Visit the following URL: {pr.html_url}")

    return pr.html_url, pr.number

def is_python_file(filename):
    return filename.lower().endswith('.py')


def generate_code_change(owner, repo, pr_number, latency_profile):
    # flag to check if we made any code changes 
    changes_made = False
    full_directory, branch_name = go_to_branch(
        owner=owner,
        repo=repo,
        pr_number=pr_number
    )
    # get files in the pr  
    pr_files = get_pr_files(owner=owner, repo=repo, pr_number=pr_number)
    print(f'Number of files to change: {len(pr_files)}')

    for file in tqdm(pr_files):
        if is_python_file(file['filename']):
            # add directory data 
            file['local_file_path'] = os.path.join(full_directory, file['filename'])
            # get code changes 
            res = CodeChangeGenerator().get_response(file, latency_results=latency_profile)
            code_change_lol = combine_close_changes(res.changes)
            for i in code_change_lol:
                patch = LineChangeFixer().get_response(file=file, code_change_list=i)
                # get changes and update 
                apply_patch_to_file(patch, file)
            
                if patch.patch is not None:
                    changes_made = True 

    if changes_made:
        remote_branch = publish_branch(local_branch_name=branch_name, directory=full_directory)
        return remote_branch, res.title, res.description

def add_comment(owner, repo, pr_number, url, improvement_message: float):
    """Adds a comment to a PR suggesting code improvement."""
    repository = github_client.get_repo(f"{owner}/{repo}")
    pr = repository.get_pull(pr_number)
    comment = f"""
    Hey there, Profiler AI has made a few optimizations to your latest PR. 

    {improvement_message}
    
    You can see the changes in [this pull request]({url}).
    """
    pr.create_issue_comment(comment)