import json
import os
import sys
from datetime import datetime, timedelta
from functools import reduce
from typing import List

from dotenv import load_dotenv
from github import Github, GithubException
from github.Commit import Commit
from github.File import File
from github.Repository import Repository


class RepoFinder:
    def __init__(self, data_folder="../data/processed", batch_size=None):
        sys.setrecursionlimit(100000)
        self.data_folder = data_folder
        self.batch_size = batch_size
        load_dotenv()
        self.g = Github(os.getenv('GITHUB_TOKEN'))

    def get_info(self, organizations: List) -> dict:
        orgs = {}

        for org in organizations:
            print(f"=========== {org} ===========")
            processed_org = self._process_organization(org)
            orgs[org] = processed_org

        return orgs

    def _process_organization(self, org: str) -> dict:
        repos = {}
        paginated_list = self.g.search_repositories(query="user:{}".format(org))
        for repo in paginated_list:
            filename = f"{self.data_folder}/{org.lower()}/{org.lower()}.{repo.name.lower()}.json"
            print(f"    === {org}/{repo.name} ===")

            processed_repo = self._process_repo(repo)
            if processed_repo is not None:
                with open(filename, "w") as f:
                    print(f"        Saving to {filename}")
                    json.dump(processed_repo, f, indent=4)

                repos[repo.name] = processed_repo
        return repos

    def _process_repo(self, repo: Repository) -> dict or None:
        if self._has_11percent_of_iac(repo) and self._has_atleast_2_commits_per_month(repo):
            commits = None
            try:
                commits = repo.get_commits()
            except GithubException:
                commits = []

            processed_commits = []

            for commit in commits if not self.batch_size else commits[0:self.batch_size]:
                processed_commits.append(self._process_commit(commit))

            return {
                "commits": processed_commits,
                "numberOfCommits": commits.totalCount
            }
        return None

    def _process_commit(self, commit: Commit) -> dict:
        files_changed = []
        processed_commit = None
        for file in commit.files:
            files_changed.append(self._process_file(file))

        try:
            processed_commit = {
                "sha": commit.sha,
                "filesChanges": files_changed
            }
        except GithubException:
            processed_commit = {
                "sha": None,
                "filesChanges": []
            }
        return processed_commit

    def _process_file(self, file: File) -> dict:
        return {
            "filename": file.filename,
            "numberOfChanges": file.changes,
            "isIaC": self._is_iac(file.filename)
        }

    def _has_11percent_of_iac(self, repo: Repository) -> bool:
        def get_file_names_recursive(path=""):
            stack = [path]
            file_names = []

            while stack:
                current_path = stack.pop()
                contents = []
                try:
                    contents = repo.get_contents(current_path)
                except GithubException:
                    print(f"        Repository is empty ({repo.name})")

                for content in contents:
                    if content.type == 'file':
                        file_names.append(content.name)
                    elif content.type == 'dir':
                        subdir_path = f"{current_path}/{content.name}" if current_path else content.name
                        stack.append(subdir_path)

            return file_names

        files = get_file_names_recursive("")
        if len(files) > 0:
            num_iac_files = len(list(filter(lambda x: self._is_iac(x), files)))
            percentage_iac = num_iac_files / len(files)
            has_11percent = percentage_iac > 0.11
            if not has_11percent:
                print(f"        ❌ {percentage_iac}% of IaC files in repo ({num_iac_files} / {len(files)})")
            return has_11percent
        return False

    def _has_atleast_2_commits_per_month(self, repo: Repository) -> bool:
        # Step 3: Calculate the number of commits per month
        creation_date = repo.created_at

        def months_between(start_date: datetime, end_date: datetime):
            current_date = start_date.replace(day=1)  # Set day to 1 to ensure we start at the beginning of a month

            while current_date <= end_date:
                yield current_date
                # Calculate the first day of the next month
                next_month = current_date.month + 1 if current_date.month < 12 else 1
                next_year = current_date.year + 1 if next_month == 1 else current_date.year
                current_date = current_date.replace(year=next_year, month=next_month, day=1)

        # Iterate over the months
        for month_start_date in months_between(creation_date, datetime.now(creation_date.tzinfo)):
            # Calculate the end of the month
            next_month = month_start_date.month + 1 if month_start_date.month < 12 else 1
            next_year = month_start_date.year + 1 if next_month == 1 else month_start_date.year
            month_end_date = (
                        month_start_date.replace(year=next_year, month=next_month, day=1) - timedelta(days=1)).replace(
                hour=23, minute=59, second=59)

            months_commits = repo.get_commits(since=month_start_date, until=month_end_date).totalCount
            if months_commits < 2:
                print(f"        ❌ Has less than 2 commits between {month_start_date.strftime('%d-%m-%Y')} and {month_end_date.strftime('%d-%m-%Y')}")
                return False

        return True

    @staticmethod
    def _is_iac(filename: str) -> bool:
        keywords = [".pp", "docker", "travis", "infra", "puppet"]
        return reduce(lambda before, keyword: keyword in filename.lower() or before, keywords, True)


# RepoFinder().get_info(["Mirantis", "wikimedia"])
