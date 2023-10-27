import datetime
import json
import os

import pandas as pd
import requests
from codetiming import Timer
from dotenv import load_dotenv
from github import Github, GithubException
from github.Commit import Commit
from github.PaginatedList import PaginatedList
from github.Repository import Repository
from dateutil.relativedelta import relativedelta


class RepoExtractor:

    def __init__(self, data_folder="../data/processed", batch_size=None):
        self.data_folder = data_folder
        self.batch_size = batch_size
        load_dotenv()
        self.api = Github(os.getenv('GITHUB_TOKEN_THOM'))
        self.timer = Timer()

    def _get_orgs_repos(self, name: str) -> PaginatedList[Repository]:
        repositories = self.api.search_repositories(query="user:{}".format(name))
        print(f"Organization '{name}' has {repositories.totalCount} repositories")
        return repositories

    def get_repo(self, fullname: str) -> Repository:
        return self.api.get_repo(fullname)

    def extract_repo_names(self, organization: str) -> list[Repository]:
        paginated_list = self._get_orgs_repos(organization)

        filename = f"{self.data_folder}/{organization}/repos.json"
        repos: list[Repository] = []
        for repo in paginated_list:
            print(repo)
            repos.append(repo)
        with open(filename, "w") as f:
            print(f"    Saving to {filename}")
            json.dump(list(map(lambda r: self.__format_repo(r), repos)), f, indent=4)
        return repos

    def extract_repo_with_fullname(self, name: str) -> list[Commit]:
        print(f"        {self.timer.stop}")
        self.timer = Timer()
        self.timer.start()
        repo = self.api.get_repo(name)
        return self.extract_repo(repo, name.split("/")[0].lower())

    def extract_repo(self, repo: Repository, org_name: str, since = None):
        processed = {}
        print(f"    Extracting commits from repo '{repo.name}'")
        commits = []
        get_commits = repo.get_commits(since=since)
        print(f"    {get_commits.totalCount} commits total")
        for c in get_commits:
            commits.append(c)
            processed[c.sha] = {
                "files": list(map(lambda file: file.filename, c.files)),
            }
        df = pd.DataFrame.from_dict(processed, orient="index")
        complete_save_path = f"{self.data_folder}/{org_name}/commits-files/{repo.name}.commits.pickle"
        print(f"        Saving commits to {complete_save_path}")
        df.to_pickle(complete_save_path)
        return commits

    def extract_repos_from_organization(self, organization_name: str, repos_to_ignore=None):
        if repos_to_ignore is None:
            repos_to_ignore = []
        extracted_repos = []
        for repo in self._get_orgs_repos(organization_name):
            if repo.full_name not in repos_to_ignore:
                extracted_repos.append(self.extract_repo(repo, organization_name))
        return repos_to_ignore

    @staticmethod
    def get_commits_url(repo_fullname: str, page: int):
        return f"https://api.github.com/repos/{repo_fullname}/commits?per_page=100&page={page}"

    def extract_raw_commits_from_repo(self, repo_fullname):
        load_dotenv()
        try:
            total_commits = self.api.get_repo(repo_fullname).get_commits().totalCount
        except GithubException:
            print(f"{repo_fullname} is empty")
            return []

        commits = []
        for i in range(int(total_commits / 100)):
            cs = requests.get(self.get_commits_url(repo_fullname, i + 1),
                              headers={"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}).json()
            commits.extend(cs)

        with open(f"../data/raw/{repo_fullname.lower()}.commits.json", "w") as file:
            json.dump(commits, file)
        return commits

    def save_commits_messages_dates(self, raw_path: str, org: str, repo: str):
        with open(f"{raw_path}") as file:
            data = json.load(file)
        ps = {}
        for d in data:
            try:
                processed = {
                    "message": d["commit"]["message"],
                    "date": d["commit"]["committer"]["date"]
                }
                ps[d["sha"]] = processed
            except Exception as e:
                print(f"{e}")
                print(raw_path)
                print(repo)
                print(d)
                print(d["commit"])
                print(d["commit"]["message"])

        if (ps.keys().__len__() == 0):
            return
        
        try:
            df = pd.DataFrame.from_dict(ps, orient="index")
            df.to_pickle(f'{self.data_folder}/{org}/commits-messages-dates/{repo}.pickle')
        except Exception as e:
            print(f"{e}")
            print(ps)
            print(raw_path)
            print(repo)

        return df

    def __format_repo(self, repo: Repository) -> dict:
        name = repo.name
        owner = repo.owner.login
        timestamp: datetime = repo.created_at
        
        if not name or not timestamp or not owner:
            # Handle cases where 'name' or 'timestamp' is missing
            return None

        # Create the output dictionary
        formated_repo = {
            'name': name,
            'owner': owner,
            'created_at': {
                'day': timestamp.day,
                'month': timestamp.month,
                'year': timestamp.year
            },
        }

        return formated_repo