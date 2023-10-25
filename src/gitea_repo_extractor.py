import json
import os

import pandas as pd
import requests
from codetiming import Timer
from dotenv import load_dotenv
import giteapy
from giteapy import SearchResults
from datetime import datetime

class GiteaRepoExtractor:

    def __init__(self, api_url, data_folder="../data/processed", batch_size=None):
        self.data_folder = data_folder
        self.batch_size = batch_size
        self.api_url = api_url
        load_dotenv()

        self.configuration = giteapy.Configuration()
        self.configuration.host = self.api_url
        self.repo_api = giteapy.RepositoryApi(giteapy.ApiClient(self.configuration))

        self.timer = Timer()

    def _get_orgs_repos(self) -> SearchResults:
        repos = []
        page = 1

        while True:
            try:
                result: SearchResults = self.repo_api.repo_search(page=page, limit=50)
                repos.extend(result.to_dict()["data"])
                if len(result.data) == 0:
                    break

                page += 1

            except giteapy.rest.ApiException as e:
                print(f"Exception when calling API {e}")
                break

        print(f"API call on '{self.api_url}' has {len(repos)} repositories")
        return repos
    
    def extract_repos_from_org(self, org_name: str, repos: SearchResults | None = None) -> list:
        if repos is None:
            repos = self._get_orgs_repos()

        filename = f"{self.data_folder}/{org_name}/repos.json"

        if(not os.path.exists(f"{self.data_folder}/{org_name}")):
            os.makedirs(f"{self.data_folder}/{org_name}")

        with open(filename, "w") as f:
            print(f"    Saving to {filename}")
            json.dump(list(map(lambda r: self.__format_repo(r), repos)), f, indent=4)
        return repos

    def __format_repo(self, repo: dict) -> dict:
        name = repo.get('name')
        timestamp: datetime = repo.get('created_at')
        
        if not name or not timestamp:
            # Handle cases where 'name' or 'timestamp' is missing
            return None

        # Create the output dictionary
        formated_repo = {
            'name': name,
            'created_at': {
                'day': timestamp.day,
                'month': timestamp.month,
                'year': timestamp.year
            }
        }

        return formated_repo

    # def get_repo(self, fullname: str) -> Repository:
    #     return self.api.get_repo(fullname)

    # def extract_repo_names(self, organization: str) -> list[Repository]:
    #     paginated_list = self._get_orgs_repos(organization)

    #     filename = f"{self.data_folder}/{organization}/repos.json"
    #     repos: list[Repository] = []
    #     for repo in paginated_list:
    #         repos.append(repo)
    #     with open(filename, "w") as f:
    #         print(f"    Saving to {filename}")
    #         json.dump(list(map(lambda r: r.full_name, repos)), f, indent=4)
    #     return repos

    # def extract_repo_with_fullname(self, name: str) -> list[Commit]:
    #     print(f"        {self.timer.stop}")
    #     self.timer = Timer()
    #     self.timer.start()
    #     repo = self.api.get_repo(name)
    #     return self.extract_repo(repo, name.split("/")[0].lower())

    # def extract_repo(self, repo: Repository, org_name: str):
    #     processed = {}
    #     print(f"    Extracting commits from repo '{repo.name}'")
    #     commits = []
    #     get_commits = repo.get_commits()
    #     print(f"    {get_commits.totalCount} commits total")
    #     for c in get_commits:
    #         commits.append(c)
    #         processed[c.sha] = {
    #             "files": list(map(lambda file: file.filename, c.files)),
    #         }
    #     df = pd.DataFrame.from_dict(processed, orient="index")
    #     complete_save_path = f"{self.data_folder}/{org_name}/commits-files/{repo.name}.commits.pickle"
    #     print(f"        Saving commits to {complete_save_path}")
    #     df.to_pickle(complete_save_path)
    #     return commits

    # def extract_repos_from_organization(self, organization_name: str, repos_to_ignore=None):
    #     if repos_to_ignore is None:
    #         repos_to_ignore = []
    #     extracted_repos = []
    #     for repo in self._get_orgs_repos(organization_name):
    #         if repo.full_name not in repos_to_ignore:
    #             extracted_repos.append(self.extract_repo(repo, organization_name))
    #     return repos_to_ignore

    # @staticmethod
    # def get_commits_url(repo_fullname: str, page: int):
    #     return f"https://api.github.com/repos/{repo_fullname}/commits?per_page=100&page={page}"

    # def extract_raw_commits_from_repo(self, repo_fullname):
    #     load_dotenv()
    #     try:
    #         total_commits = self.api.get_repo(repo_fullname).get_commits().totalCount
    #     except GithubException:
    #         print(f"{repo_fullname} is empty")
    #         return []

    #     commits = []
    #     for i in range(int(total_commits / 100)):
    #         cs = requests.get(self.get_commits_url(repo_fullname, i + 1),
    #                           headers={"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}).json()
    #         commits.extend(cs)

    #     with open(f"../data/raw/{repo_fullname.lower()}.commits.json", "w") as file:
    #         json.dump(commits, file)
    #     return commits

    # def save_commits_messages_dates(self, raw_path: str, org: str, repo: str):
    #     with open(f"{raw_path}") as file:
    #         data = json.load(file)
    #     ps = {}
    #     for d in data:
    #         processed = {
    #             "message": d["commit"]["message"],
    #             "date": d["commit"]["committer"]["date"]
    #         }
    #         ps[d["sha"]] = processed

    #     df = pd.DataFrame.from_dict(ps, orient="index")
    #     df.to_pickle(f'{self.data_folder}/{org}/commits-messages-dates/{repo}.pickle')
    #     return df
