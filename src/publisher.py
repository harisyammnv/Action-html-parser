from github import Github
from parser import parse_reports
import os

options = dict(os.environ)


g = Github(options["GITHUB_TOKEN"])
repo_name = 'harisyammnv/html-parser'
repo = g.get_repo(repo_name)
pr = repo.get_pull(1)
result = parse_reports()
pr.create_issue_comment(result)

