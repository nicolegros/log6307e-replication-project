from datetime import datetime, timedelta
from functools import reduce
import os
from github import Github

import numpy as np
import pandas as pd


class CommitMessageProcesser:
    def __init__(self, repo_name: str, data_folder="../data/processed"):
        self.data_folder = data_folder
        self.repo_name = repo_name

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
