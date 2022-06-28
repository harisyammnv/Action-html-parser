from github import Github
import os

options = dict(os.environ)


g = Github(options["GITHUB_TOKEN"])
repo_name = '/repo'
repo = g.get_repo(repo_name)
pr = repo.get_pull()
pr.create_issue_comment('test')

