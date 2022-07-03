from github import Github
import os
from pathlib import Path
import json
from src.parser import parse_reports

options = dict(os.environ)

def append_to_file(content: str, env_file_var_name: str):
    # appends content to an environment file denoted by an environment variable name
    # https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#environment-files
    with open(Path.cwd().joinpath(env_file_var_name), 'w', encoding='utf-8') as file:
        file.write(content)

g = Github(options["GITHUB_TOKEN"])
repo_name = options["GITHUB_REPOSITORY"]
repo = g.get_repo(repo_name)
pulls = repo.get_pulls(state="open", sort='created')
for pull in pulls:
    print(pull)
    nr = pull.number
pr = repo.get_pull(nr)
summary, result = parse_reports(options)

pr.create_issue_comment(result)

markdown = f"## Code Quality Results\n{summary}"
append_to_file(content = markdown, env_file_var_name=options["SUMMARY_FILE_NAME"].strip(".md")+"-summary.md")

markdown = f"## Code Quality Results\n{summary} \n ### File Results \n{result}"
append_to_file(content = markdown, env_file_var_name=options["SUMMARY_FILE_NAME"])