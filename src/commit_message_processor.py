from datetime import datetime, timedelta
from functools import reduce
import os
import re
from github import Github

import numpy as np
import pandas as pd
import json

import requests


class CommitMessageProcessor:
    def __init__(self, data_folder="../data/processed"):
        self.data_folder = data_folder
        self.issue_identifier_pattern = re.compile(r"#\d{1,10}")
        self.api = Github(os.getenv('GITHUB_TOKEN'))

    def extract_xcm(self, org: str, repo_name: str) -> list :
        self.commits_df: pd.DataFrame = pd.read_pickle(f"{self.data_folder}/{org}/commits-files/{repo_name}.commits.pickle")
        self.commit_messsage_df: pd.DataFrame = pd.read_pickle(f"{self.data_folder}/{org}/commits-messages-dates/{repo_name}.pickle")
        print(f"    Extracting XCM from repo '{repo_name}'")
        print(f"   {self.commits_df.size} commits total")

        xcms: list[dict] = []
        for sha in self.commits_df.index:
            if (not self.__commit_modifies_iac(sha)):
                continue

            commit_message = self.__extract_commit_message(sha)
            issue_identifier = self.__extract_issue_identifier(commit_message)
            issue_summary = ""
            if issue_identifier:
                try:
                    issue = requests.get(self.get_issue_url(org, repo_name, issue_identifier)).json()
                except requests.RequestException as e:
                    print(f"{e}")
                    issue = None

                issue_summary = issue["body"] if issue and "body" in issue else ""
            xcm = self.__convert_to_xcm(commit_message, issue_summary)
            xcms.append(xcm)

        complete_save_path = f"{self.data_folder}/{org}/xcms/{repo_name}.json"
        print(f"        Saving xcms to {complete_save_path}")
        with open(complete_save_path, "w") as f:
            json.dump(xcms, f, indent=4)
        
        return xcms
    
    def __commit_modifies_iac(self, commit_sha: str) -> bool:
        return reduce(lambda before, file: self._is_iac(file) or before, self.commits_df.loc[commit_sha].files, False)
    
    def __extract_commit_message(self, commit_sha: str) -> str: 
        if commit_sha not in self.commit_messsage_df.index:
            return ""
        
        return self.commit_messsage_df.loc[commit_sha].message
    
    def __extract_issue_identifier(self, commit_message: str) -> str | None:
        issue_identifier = None
        match = self.issue_identifier_pattern.search(commit_message)
        if match:
            issue_identifier = match.group(0)

        return issue_identifier
    
    def __convert_to_xcm(self, commit_message: str, issue_summary: str) -> dict:
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
