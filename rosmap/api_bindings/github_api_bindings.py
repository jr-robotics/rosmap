import json
import logging
import time
import certifi

import urllib3

PAGE_SIZE = 100
TOPIC_SEARCH_URL = 'https://api.github.com/search/repositories?q=topic%3A'


class GithubApiBindings:
    """
    Wraps GitHub API functions.
    """
    def __init__(self, username: str, password: str, rate_limit: float):
        """
        Creates a new instance of the GithubApiBindings Class.
        :param username: Username to log into GitHub
        :param password: Password to log into GitHub
        :param rate_limit: GitHub API rate limit (requests per hour)
        """
        self.__username = username
        self.__password = password
        self.__rate_limit = rate_limit

    def __form_github_request(self, url: str) -> urllib3.response:
        """
        Forms a request for the GitHub API.
        :param url: Request URL
        :return: Response
        """
        time.sleep(3600/self.__rate_limit)
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        return http.request('GET',
                            url,
                            headers=urllib3.util.make_headers(basic_auth=self.__username + ":" + self.__password,
                                                              user_agent=self.__username))

    def __get_page(self, topic: str, pagesize: int, page: int, ascending: bool) -> dict:
        """
        Gets a page from GitHub Search API.
        :param topic: The topic to serach for.
        :param pagesize: Amount of results this page should yield.
        :param page: Page number.
        :param ascending: sort ascending (true) or descending (false)
        :return: deserialized json string as dict.
        """
        url = TOPIC_SEARCH_URL + topic + '&per_page=' + str(pagesize) + '&page=' + str(page)
        if ascending:
            response = self.__form_github_request(url + "&sort=stars&order=asc")
        else:
            response = self.__form_github_request(url + "&sort=stars&order=dsc")
        if response.status == 200:
            return json.loads(response.data.decode('utf-8'))
        else:
            return json.loads('{"items":{}}')

    def get_urls_of_topic(self, topic: str) -> set:
        """
        Fetches all repository URLs form GitHub API.
        :param topic: The topic to search for.
        :return: A set of all repository URLs.
        """
        page = 1
        logging.info('[Github API Connector]: Fetching all repository-URLs with topic ' + topic + ' from Github...')

        # Fetch first page.
        data_asc = self.__get_page(topic, PAGE_SIZE, page, True)

        # Get number of repositories and calculate page size, since non-authenticated GitHub Search API only allows 10
        # requests per Minute.
        repository_count = data_asc["total_count"]

        if repository_count <= 1000:
            logging.info("[Github API Connector]: Number of total repositories: " + str(repository_count))
        else:
            logging.warning("[Github API Connector]: " +
                            "GitHub API only allows <=1k results. " +
                            "Will try to get all items by iterating multiple times.")

        repositories = set()

        old_repository_count = -1
        while len(repositories) > old_repository_count:
            old_repository_count = len(repositories)

            # Fetch next page.
            logging.info('[Github API Connector]: Parsing GitHub clone-URLs... [' + str(len(repositories)) + '/' + str(repository_count) + ']')

            # Add all items on current page.
            for repository in self.__get_page(topic, PAGE_SIZE, page, True)["items"]:
                repositories.add(repository["clone_url"])

            if repository_count > 1000:
                # Also iterate descending.
                # Add all items on current page.
                for repository in self.__get_page(topic, PAGE_SIZE, page, False)["items"]:
                    repositories.add(repository["clone_url"])

            page += 1

        logging.info('[Github API Connector]: Progress... ['
                     + str(len(repositories))
                     + '/' + str(repository_count) + ']')

        # Return all repositories.
        return repositories

    def __extract_next_url_from_header(self, header: dict) -> str:
        """
        Extracts the next page URL from a GitHub API response header.
        :param header: The header from a GitHub API request.
        :return: Empty string if no next link is available, next link if the link is available.
        """
        try:
            links = header["Link"].split(",")
            for link in links:
                if 'rel="next"' in link:
                    return link.split(">;")[0].split("<")[1]
        except:
            logging.info("[Github API Connector]: Reached end of pages for this category. Continuing to next.")
        return ""

    def __get_repo_substring(self, url, provider) -> str:
        """
        Gets the repo-substring (i.e. url: https://github.com/ros/ros_comm.git -> returns: ros/ros_comm
        :param url: URL to get the substring from.
        :param provider: Part to cut off from the front.
        :return: the substring formatted as {<user>|<organization>}/{repository_name}
        """
        project_string = url.split(provider)[1]
        project_string = project_string.split(".git")[0]
        return project_string

    def get_issues(self, url: str, issue_state: str) -> iter:
        """
        Yield returns all issues with the specified state.
        :param url: The url to the repository to get issues from.
        :param issue_state: The issue state (most commonly OPEN or CLOSED)
        :return: Yield returns all issues with the specified state.
        """

        project_string = self.__get_repo_substring(url, "https://github.com/")
        next_uri = "https://api.github.com/repos/" + project_string + "/issues?state=" + issue_state
        while next_uri != "":
            response = self.__form_github_request(next_uri)
            if response.status != 200:
                next_uri = ""
                logging.warning("[Github API Connector]: Response returned " + str(response.status))
            else:
                data = response.data
                issues = json.loads(data.decode(response))
                for issue in issues:
                    yield issue
                next_uri = self.__extract_next_url_from_header(response.headers)

    def get_stargazer_count(self, url: str) -> int:
        """
        Returns the stargazer count for a repository.
        :param url: URL to the repository.
        :return: stargazer count for the repository. (-1 if request failed.)
        """
        project_string = self.__get_repo_substring(url, "https://github.com/")
        response = self.__form_github_request("https://api.github.com/repos/" + project_string)
        if response.status == 200:
            data = response.data
            return json.loads(data.decode('utf-8'))["stargazers_count"]
        return -1

    def is_pull_request(self, issue: dict):
        """
        returns whether issue is a pull request or not (github treats pull requests as issues)
        :param issue: the issue to check.
        :return: true if it is a pull request, false if it is not.
        """
        return "pull_request" in issue
