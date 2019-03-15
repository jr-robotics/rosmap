from .abstract_repository_analyzer import AbstractRepositoryAnalyzer
from xml.etree.cElementTree import fromstring
from xml.etree.cElementTree import ParseError
import subprocess
import os
import dateutil.parser
import logging


class SubversionRepositoryAnalyzer(AbstractRepositoryAnalyzer):
    """
    Analysis plug-in for Subversion repositories.
    """

    def count_repo_branches(self, repo_path: str, remote: str) -> None:
        """
        Counts the repository's branches.
        :param repo_path: path to the repository root.
        :param remote: remote uri of the branches
        :return: None
        """
        branches = subprocess.check_output("cd " + repo_path + ";svn ls $(svn info --show-item=repos-root-url)/branches | wc -l", shell=True)
        self.get_details(remote)["branch_count"] = int(branches)

    def count_repo_contributors(self, repo_path: str, remote:str) -> None:
        """
        Counts the repository's contributors.
        :param repo_path: path to the repository root.
        :param remote: remote uri of the branches
        :return: None
        """
        contributors = subprocess.check_output("cd " + repo_path + ";svn log --quiet | awk '/^r/ {print $3}' | sort -u | wc -l", shell=True)
        self.get_details(remote)["contributors"] = int(contributors)

    def extract_repo_url(self, repo_path) -> str:
        """
        Extracts the Remote URL from a given SVN repository-path.
        :param repo_path: path to the repository root.
        :return: Remote URL
        """
        try:
            return subprocess.check_output("cd " + repo_path + ";svn info --show-item=url", shell=True).decode("utf-8").rstrip("\n")
        except subprocess.CalledProcessError:
            return ""

    def extract_last_repo_update(self, repo_path: str, remote: str) -> None:
        """
        Extracts the repository's last update-timestamp.
        :param repo_path: path to the repository root.
        :param remote: remote uri of the branches
        :return: None
        """

        timestamp = subprocess.check_output("cd " + repo_path + ";svn log --limit 1 --incremental --xml --quiet", shell=True)

        # Parse xml
        try:
            element = fromstring(timestamp)
        except ParseError:
            logging.warning("[SubversionRepositoryAnalyzer]: Could not parse " + timestamp + "; omitting file.")
            return

        # Get actual timestamp
        timestamp = element.find('date').text
        timestamp = dateutil.parser.parse(timestamp)

        # Insert timestamp into details.
        self.get_details(remote)["last_update"] = int(timestamp.timestamp())

    def _analyze(self, path: str, repo_details: dict) -> None:
        self._repo_details = repo_details
        for folder in os.listdir(path):

            # Build path and inform user...
            current_path = path + "/" + folder + ""
            logging.info("[SubversionRepositoryAnalyzer]: Analyzing:" + current_path)

            # Extract origin url.
            origin_url = self.extract_repo_url(current_path)

            # If origin_url is "", then this is not a valid svn-repository.
            if origin_url != "":
                # Subversion analysis.
                self.count_repo_contributors(current_path, origin_url)
                self.count_repo_branches(current_path, origin_url)
                self.extract_last_repo_update(current_path, origin_url)

                yield (current_path, origin_url)
            else:
                logging.warning("[SubversionRepositoryAnalyzer]: " + current_path + " is not a valid repository...")

    def analyzes(self):
        return "svn"