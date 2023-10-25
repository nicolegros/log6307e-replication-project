from datetime import datetime, timedelta
from functools import reduce

import numpy as np
import pandas as pd


class RepoValidator:
    def __init__(self, repo_pickle_file: str):
        self.df: pd.DataFrame = pd.read_pickle(repo_pickle_file)
        print(self.df.head())

    def is_valid(self) -> bool:
        return self.has_11_percent_of_iac() and self.has_at_least_2_commits_per_month()

    def has_at_least_2_commits_per_month(self) -> bool:
        if self.df.size < 1:
            return False
        self.df.loc[:, 'month'] = pd.to_datetime(self.df.date).dt.month
        self.df.loc[:, 'year'] = pd.to_datetime(self.df.date).dt.year
        return (self.df.groupby(['year', 'month']).count() >= 2).all()["date"]

    def has_11_percent_of_iac(self) -> bool:
        list_folder = []
        for l in self.df.files.to_list():
            list_folder.extend(l)
        unique_files = np.unique(list_folder).tolist()

        is_iac_list = []
        for file in unique_files:
            is_iac_list.append(self._is_iac(file))
        return (sum(is_iac_list) / len(is_iac_list)) >= 0.11

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
