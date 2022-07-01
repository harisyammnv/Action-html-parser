from github import Github, CheckRunAnnotation
import os
from pathlib import Path
from src.parser import parse_reports
from src.github_action import *

options = dict(os.environ)

def append_to_file(content: str, env_file_var_name: str):
    # appends content to an environment file denoted by an environment variable name
    # https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#environment-files
    with open(Path.cwd().joinpath(env_file_var_name), 'w', encoding='utf-8') as file:
        file.write(content)

g = Github(options["GITHUB_TOKEN"])
repo_name = 'harisyammnv/html-parser'
repo = g.get_repo(repo_name)
pr = repo.get_pull(1)
summary, result = parse_reports()

pr.create_issue_comment(result)

markdown = f"## Code Quality Results\n{summary} \n ### File Results \n{result}"
append_to_file(content = markdown, env_file_var_name=options["FILE_NAME"])

json = {"summary": markdown}
append_to_file(content = json, env_file_var_name=options["FILE_NAME"].strip('.md')+'-result.json')