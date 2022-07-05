from github import Github
import os
from pathlib import Path
import json
from src.parser import parse_reports
from src.retry import GitHubRetry
from src.github_action import GithubAction
from urllib3.util.retry import Retry
options = dict(os.environ)

def get_github(token: str, url: str, retries: int, backoff_factor: float, gha: GithubAction):
    retry = GitHubRetry(gha=gha,
                        total=retries,
                        backoff_factor=backoff_factor,
                        allowed_methods=Retry.DEFAULT_ALLOWED_METHODS.union({'GET', 'POST'}),
                        status_forcelist=list(range(500, 600)))
    return Github(login_or_token=token, base_url=url, per_page=100, retry=retry)

def append_to_file(content: str, env_file_var_name: str):
    # appends content to an environment file denoted by an environment variable name
    # https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#environment-files
    with open(Path.cwd().joinpath(env_file_var_name), 'w', encoding='utf-8') as file:
        file.write(content)

gha = GithubAction()
seconds_between_github_reads = 1
seconds_between_github_writes = 2
backoff_factor = max(seconds_between_github_reads, seconds_between_github_writes)
g = get_github(token=options["GITHUB_TOKEN"], 
               url=options['GITHUB_API_URL'], 
               retries='10', 
               backoff_factor=backoff_factor, 
               gha=gha)

repo_name = options["GITHUB_REPOSITORY"]
repo = g.get_repo(repo_name)
pulls = list(repo.get_pulls(state="open", sort='created'))
pr = repo.get_pull(pulls[-1].number)
summary, result, conclusion, summary_dict = parse_reports(options)

pr.create_issue_comment(result)

repo.create_check_run(name="Code Quality Results", 
                      head_sha=options["GITHUB_SHA"],
                      status="completed",
                      conclusion=conclusion,
                      output=summary_dict)

markdown = f"## Code Quality Results\n{summary}"
append_to_file(content = markdown, env_file_var_name=options["SUMMARY_FILE_NAME"].strip(".md")+"-summary.md")

markdown = f"## Code Quality Results\n{summary} \n ### File Results \n{result}"
append_to_file(content = markdown, env_file_var_name=options["SUMMARY_FILE_NAME"])