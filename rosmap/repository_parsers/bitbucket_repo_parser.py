import logging
from pyquery import PyQuery
from urllib.error import HTTPError
from .i_repository_parser import IRepositoryParser


class BitbucketRepositoryParser(IRepositoryParser):
    """
    Parses repository-URLs from Bitbucket using the Bitbucket-search.
    """

    def __init__(self, settings):
        """
        Creates a new instance for the BitbucketRepositoryParser-class.
        :param settings: Settings dict containing keys bitbucket_repo_page, and bitbucket_repo_search_string.
        """
        self.__settings = settings

    def parse_repositories(self, repository_dict: dict) -> None:
        links = set()
        page_number = 0
        previous_length = -1

        # Add links until there aren't any links left to add.
        while len(links) != previous_length:
            page_number += 1
            previous_length = len(links)

            # Get page.
            d = PyQuery(url=self.__settings["bitbucket_repo_page"]
                            + str(page_number)
                            + '?name='
                            + self.__settings["bitbucket_repo_search_string"])

            # Iterate over every element of class .repo-link
            for item in d(".repo-link").items():
                links.add('https://bitbucket.org' + item.attr("href"))

            # Print progress information.
            logging.info("[BitbucketRepoParser]: Parsing BitBucket links... [" + str(len(links)) + " items]")

        # extract actual links to the repositories.
        progress_counter = 0
        for link in links:
            progress_counter += 1
            try:
                # get every item of .clone-url-input class.
                d = PyQuery(url=link)
                for item in d(".clone-url-input").items():
                    # get URL
                    url = str(item.attr("value"))

                    # make sure URL is not a wiki-URL
                    if url[-4:] != "wiki":
                        # extract vcs type from the back of the URL.
                        vcs_type = url.split('.')[-1]
                        if vcs_type != "git":
                            vcs_type = "hg"
                        # add url to the vcs-type's list.
                        repository_dict[vcs_type].add(url)

                # Print progress information.
                logging.info("[BitbucketRepoParser]: Parsing BitBucket clone-URLs... ["
                             + str(progress_counter) + "/" + str(len(links)) + "]")
            except HTTPError as error:
                # Notify user of error.
                logging.warning("[BitbucketRepoParser]: Could not parse from " + link + ", " + error.reason)
