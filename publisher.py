from github import Github
import os
from pathlib import Path
import json
from src.parser import parse_reports
from src.retry import GitHubRetry
from src.github_action import GithubAction
from urllib3.util.retry import Retry
from typing import *
options = dict(os.environ)

def get_var(name: str, options: dict) -> Optional[str]:
    """
    Returns the value from the given dict with key 'INPUT_$key',
    or if this does not exist, key 'key'.
    """
    # the last 'or None' turns empty strings into None
    return options.get(f'INPUT_{name}') or options.get(name) or None

def check_var(var: Union[Optional[str], List[str]],
              name: str,
              label: str,
              allowed_values: Optional[List[str]] = None,
              deprecated_values: Optional[List[str]] = None) -> None:
    if var is None:
        raise RuntimeError(f'{label} must be provided via action input or environment variable {name}')

    if allowed_values:
        if isinstance(var, str):
            if var not in allowed_values + (deprecated_values or []):
                raise RuntimeError(f"Value '{var}' is not supported for variable {name}, "
                                   f"expected: {', '.join(allowed_values)}")
        if isinstance(var, list):
            if any([v not in allowed_values + (deprecated_values or []) for v in var]):
                raise RuntimeError(f"Some values in '{', '.join(var)}' "
                                   f"are not supported for variable {name}, "
                                   f"allowed: {', '.join(allowed_values)}")
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

def get_commit_sha(event: dict, event_name: str, options: dict):
    print(f"action triggered by '{event_name}' event")

    # https://developer.github.com/webhooks/event-payloads/
    if event_name.startswith('pull_request'):
        return event.get('pull_request', {}).get('head', {}).get('sha')

    # https://docs.github.com/en/free-pro-team@latest/actions/reference/events-that-trigger-workflows
    return options.get('GITHUB_SHA')

gha = GithubAction()
seconds_between_github_reads = 1
seconds_between_github_writes = 2
backoff_factor = max(seconds_between_github_reads, seconds_between_github_writes)
g = get_github(token=options["GITHUB_TOKEN"], 
               url=options['GITHUB_API_URL'], 
               retries='10', 
               backoff_factor=backoff_factor, 
               gha=gha)

event_file = get_var('EVENT_FILE', options)
event = event_file or get_var('GITHUB_EVENT_PATH', options)
event_name = get_var('EVENT_NAME', options) or get_var('GITHUB_EVENT_NAME', options)
check_var(event, 'GITHUB_EVENT_PATH', 'GitHub event file path')
check_var(event_name, 'GITHUB_EVENT_NAME', 'GitHub event name')
with open(event, 'rt', encoding='utf-8') as f:
    event = json.load(f)

repo_name = options["GITHUB_REPOSITORY"]
repo = g.get_repo(repo_name)
pulls = list(repo.get_pulls(state="open", sort='created'))
pr = repo.get_pull(pulls[-1].number)
summary, result, conclusion = parse_reports(options)

pr.create_issue_comment(result)

markdown = f"## Code Quality Results\n{summary}"
full_markdown = f"## Code Quality Results\n{summary} \n ### File Results \n{result}"

summary_dict = {}
summary_dict["title"] = "Code Quality Check"
summary_dict["summary"] = markdown
summary_dict["text"] = f"### File Results \n{result}"

repo.create_check_run(name="Code Quality Results", 
                      head_sha=get_commit_sha(event, event_name, options),
                      status="completed",
                      conclusion=conclusion,
                      output=summary_dict)

append_to_file(content = markdown, env_file_var_name=options["SUMMARY_FILE_NAME"].strip(".md")+"-summary.md")
append_to_file(content = full_markdown, env_file_var_name=options["SUMMARY_FILE_NAME"])