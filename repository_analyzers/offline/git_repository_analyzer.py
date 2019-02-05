from .abstract_repository_analyzer import AbstractRepositoryAnalyzer
from git import Repo
from git import InvalidGitRepositoryError
import subprocess
import os
import logging


class GitRepositoryAnalyzer(AbstractRepositoryAnalyzer):
    """
    Analysis plug-in for Git-Repositories.
    """

    def count_repo_branches(self, repo_path: str, remote: str) -> None:
        """
        Counts the repository's branches.
        :param repo_path: path to the repository root.
        :param remote: remote uri of the branches
        :return: None
        """
        branches = subprocess.check_output("cd " + repo_path + ";git branch -a | wc -l", shell=True)
        self.get_details(remote)["branch_count"] = int(branches)

    def count_repo_contributors(self, repo_path: str, remote: str) -> None:
        """
        Counts the repository's contributors.
        :param repo_path: path to the repository root.
        :param remote: remote uri of the branches
        :return: None
        """
        contributors = subprocess.check_output("cd " + repo_path + ";git shortlog -s HEAD | wc -l", shell=True)
        self.get_details(remote)["contributors"] = int(contributors)

    def extract_last_repo_update(self, repo_path: str, remote: str) -> None:
        """
        Extracts the repository's last update-timestamp.
        :param repo_path: path to the repository root.
        :param remote: remote uri of the branches
        :return: None
        """
        timestamp = subprocess.check_output("cd " + repo_path + ";git log -1 --format=%ct", shell=True)
        self.get_details(remote)["last_update"] = int(timestamp)

    def _analyze(self, path: str, repo_details: dict) -> iter:
        self._repo_details = repo_details
        for folder in os.listdir(path):

            # Build path and inform user...
            current_path = path + "/" + folder + ""
            logging.info("[GitRepositoryAnalyzer]: Analyzing:" + current_path)

            # Check if repo is valid.
            try:
                repo = Repo(path + "/" + folder + "/")
            except InvalidGitRepositoryError:
                continue

            # Extract origin url.
            origin_url = repo.remotes.origin.url

            # Git analysis.
            self.count_repo_contributors(current_path, origin_url)
            self.count_repo_branches(current_path, origin_url)
            self.extract_last_repo_update(current_path, origin_url)

            yield (current_path, origin_url)

    def analyzes(self):
        return "git"
