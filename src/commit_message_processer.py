from datetime import datetime, timedelta
from functools import reduce
import os
import re
from github import Github

import numpy as np
import pandas as pd


class CommitMessageProcesser:
    def __init__(self, repo_name: str, data_folder="../data/processed"):
        self.data_folder = data_folder
        self.repo_name = repo_name
        # Write and store a regex pattern that matches any string that starts with a # followed by up to 10 numbers and returns the first match
        self.issue_identifier_pattern = re.compile(r"#\d{1,10}")

        self.commits_df: pd.DataFrame = pd.read_pickle(f"{self.data_folder}/{self.repo_name}.commits.pickle")
        self.commit_messsage_df: pd.DataFrame = pd.read_pickle(f"{self.data_folder}/{self.repo_name}.pickle")
        print(self.commits_df.head())
        print(self.commit_messsage_df.head())

        self.api = Github(os.getenv('GITHUB_TOKEN'))
        self.api.search_issues(query="repo:{}".format(self.repo_name))

    def commit_modifies_iac(self, commit_sha: str) -> bool:
        return self.commits_df.loc[commit_sha].files.apply(lambda file: self._is_iac(file)).any()
    
    def extract_commit_message(self, commit_sha: str) -> str: 
        return self.commit_messsage_df.loc[commit_sha].message
    
    def extract_issue_identifier(self, commit_message: str) -> str | None:
        issue_identifier = None
        match = self.issue_identifier_pattern.search(commit_message)
        if match:
            issue_identifier = match.group(0)

        return issue_identifier
    
    def convert_to_xcm(commit_message: str, issue_summary: str) -> dict:
        return {
            "commit_message": commit_message,
            "issue_summary": issue_summary
        }

    @staticmethod
    def get_issue_url(owner: str, repo: str, issue_number: str) -> str:
        return f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    
    @staticmethod
    def _is_iac(filename: str) -> bool:
        keywords = [".pp",
                    "docker",
                    "travis",
                    "infra",
                    "puppet",
                    "k8s",
                    "environment",
                    "kubernetes"]
        return reduce(lambda before, keyword: keyword in filename.lower() or before, keywords, False)
