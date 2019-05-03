import json
import logging
import time
import certifi
import urllib3


class BitbucketApiBindings:
    """
    Wraps Bitbucket API functions.
    """
    def __init__(self, rate_limit: int):
        self.__rate_limit = rate_limit

    def form_bitbucket_request(self, url: str) -> urllib3.response:
        """
        Creates new bitbucket request and returns the response.
        :param url: The url to call.
        :return: The response resulting from the request.
        """
        time.sleep(3600/self.__rate_limit)
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        return http.request('GET',
                            url)

    def get_repo_substring(self, url, provider):
        """
        Gets the repo-substring (i.e. url: https://bitbucket.org/osrf/gazebo -> returns: osrf/gazebo
        :param url: URL to get the substring from.
        :param provider: Part to cut off from the front.
        :return: the substring formatted as {<user>|<organization>}/{repository_name}
        """

        project_string = url.split(provider)[1]
        # This is okay since Mercurial does not have an extension on the back of remote urls.
        project_string = project_string.split(".git")[0]
        return project_string

    def get_stargazer_count(self, repo_url):
        """
        Gets the "stargazer" count for github. Used watchers since stargazers do not exist in Bitbucket.
        :param repo_url: URL to the repository.
        :return: the amount of watchers on the repository, -1 if request failed.
        """
        project_string = self.get_repo_substring(repo_url, "https://bitbucket.org/")
        response = self.form_bitbucket_request(
            "https://api.bitbucket.org/2.0/repositories/" + project_string + "/watchers")
        if response.status == 200:
            data = response.data
            decoded = json.loads(data.decode('utf-8'))
            return decoded["size"]
        return -1

    def get_next_url(self, result):
        """
        Gets the URL for the next page.
        :param result: URL for the next page.
        :return: The next url, or empty string, if no next string is available.
        """
        if "next" in result:
            return result["next"]
        else:
            return ""

    def get_issues_api_string(self, repo_url):
        """
        Returns API url to call for issues associated with the repository.
        :param repo_url: Repository URL to get issues from.
        :return: API URL for retrieving an issue list.
        """
        project_string = self.get_repo_substring(repo_url, "https://bitbucket.org/")
        return "https://api.bitbucket.org/2.0/repositories/" + project_string + "/issues"

    def get_pull_requests_api_string(self, repo_uri):
        """
        Returns API URL to call for (open) pull requests associated with the repository.
        :param repo_uri: Repository URL to get pull requests from.
        :return: API URL for retrieving pull request list.
        """
        project_string = self.get_repo_substring(repo_uri, "https://bitbucket.org/")
        return "https://api.bitbucket.org/2.0/repositories/" + project_string + "/pullrequests?state=OPEN"

    def get_values(self, api_url) -> iter:
        """
        Gets the values field from an Bitbucket API result (used for e.g. pull requests, issues, etc..)
        :param api_url: API url to call. (see *_api_string)
        :return: Yield returns the values from the Bitbucket API.
        """
        next_url = api_url
        while next_url != "":
            response = self.form_bitbucket_request(next_url)
            if response.status != 200:
                logging.info("[Bitbucket API Connector]: Could not reach " + next_url + ", request returned " + str(response.status))
                next_url = ""
            else:
                result = json.loads(response.data.decode('utf-8'))

                if "values" in result:
                    for value in result["values"]:
                        yield value

                next_url = self.get_next_url(result)

