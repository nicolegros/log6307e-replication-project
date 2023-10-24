import json
import os

import pandas as pd
from dotenv import load_dotenv
from github import Github
from github.Commit import Commit
from github.PaginatedList import PaginatedList
from github.Repository import Repository


class RepoExtractor:

    def __init__(self, data_folder="../data/processed", batch_size=None):
        self.data_folder = data_folder
        self.batch_size = batch_size
        load_dotenv()
        self.api = Github(os.getenv('GITHUB_TOKEN'))

    def _get_orgs_repos(self, name: str) -> PaginatedList[Repository]:
        repositories = self.api.search_repositories(query="user:{}".format(name))
        print(f"Organization '{name}' has {repositories.totalCount} repositories")
        return repositories

    def extract_repo_names(self, organization: str) -> list[Repository]:
        paginated_list = self._get_orgs_repos(organization)

        filename = f"{self.data_folder}/{organization}/repos.json"
        repos: list[Repository] = []
        for repo in paginated_list:
            repos.append(repo)
        with open(filename, "w") as f:
            print(f"    Saving to {filename}")
            json.dump(list(map(lambda r: r.full_name, repos)), f, indent=4)
        return repos

    def extract_repo_with_fullname(self, name: str) -> list[Commit]:
        repo = self.api.get_repo(name)
        return self._extract_repo(repo, name.split("/")[0].lower())

    def _extract_repo(self, repo: Repository, org_name: str):
        processed = {}
        print(f"    Extracting commits from repo '{repo.name}'")
        commits = []
        for c in repo.get_commits():
            commits.append(c)
            processed[c.sha] = {
                "files": list(map(lambda file: file.filename, c.files)),
                "date": c.commit.committer.date,
                "message": c.commit.message
            }
        df = pd.DataFrame.from_dict(processed, orient="index")
        complete_save_path = f"{self.data_folder}/{org_name}/{repo.name}.commits.pickle"
        print(f"        Saving commits to {complete_save_path}")
        df.to_pickle(complete_save_path)
        return commits

    def extract_repos_from_organization(self, organization_name: str, repos_to_ignore=None):
        if repos_to_ignore is None:
            repos_to_ignore = []
        extracted_repos = []
        for repo in self._get_orgs_repos(organization_name):
            if repo.full_name not in repos_to_ignore:
                extracted_repos.append(self._extract_repo(repo, organization_name))
        return repos_to_ignore


# ======= Run =======
RepoExtractor().extract_repos_from_organization("mirantis")
