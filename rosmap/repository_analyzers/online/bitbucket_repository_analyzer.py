import dateutil
import logging
from .i_scs_analyzer import ISCSRepositoryAnalyzer
from rosmap.api_bindings.bitbucket_api_bindings import BitbucketApiBindings


class BitbucketRepositoryAnalyzer(ISCSRepositoryAnalyzer):
    """
    Analyzes repositories remotely on Bitbucket and extracts Bitbucket-specific information.
    """
    def __init__(self, settings: dict):
        """
        Creates a new instance of the BitbucketRepositoryAnalyzer.
        :param settings: settings containing the bitbucket_api_rate_limit (requests/hour)
        """
        self.__api_bindings = BitbucketApiBindings(settings["bitbucket_api_rate_limit"])

    @staticmethod
    def initialize_values(repo_details: dict) -> None:
        """
        Initializes all values that might be needed in order to avoid exceptions.
        :param repo_details: details associated with the analyzed repository.
        :return:
        """

        if "issue_durations" not in repo_details:
            repo_details["issue_durations"] = list()
        if "open_pull_requests" not in repo_details:
            repo_details["open_pull_requests"] = 0
        if "open_issues" not in repo_details:
            repo_details["open_issues"] = 0

    def count_stargazers(self, repo_uri: str, details: dict) -> None:
        """
        Counts all stargazers.
        :param repo_uri: The URL to the repository.
        :param details: The Details associated with the URL.
        :return: None
        """
        details["stars"] = self.__api_bindings.get_stargazer_count(repo_uri)

    def count_issues(self, repo_uri: str, details: dict) -> None:
        """
        Counts open and closed issues.
        :param repo_uri: The URL to the repository.
        :param details: The Details associated with the URL.
        :return: None
        """
        for issue in self.__api_bindings.get_values(self.__api_bindings.get_issues_api_string(repo_uri)):
            if issue["state"] in ["open", "new"]:
                details["open_issues"] += 1
            else:
                elapsed_time = dateutil.parser.parse(issue["updated_on"]) - dateutil.parser.parse(issue["created_on"])
                details["issue_durations"].append(elapsed_time.total_seconds())

    def count_pull_requests(self, repo_uri: str, details: dict) -> None:
        """
        Counts open pull requests.
        :param repo_uri: The URL to the repository.
        :param details: The Details associated with the URL.
        :return: None
        """
        for pull_request in self.__api_bindings.get_values(self.__api_bindings.get_pull_requests_api_string(repo_uri)):
            if pull_request["state"] == "OPEN":
                details["open_pull_requests"] += 1

    def analyze_repositories(self, repo_details: dict) -> None:
        for url, details in repo_details.items():
            if "bitbucket" in url:
                logging.info("[BitbucketRepositoryAnalyzer]: Fetching data from " + url)
                self.count_stargazers(url, details)
                self.count_issues(url, details)
                self.count_pull_requests(url, details)

    def analyzes(self):
        return "bitbucket"