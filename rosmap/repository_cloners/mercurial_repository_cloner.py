from .i_repository_cloner import IRepositoryCloner
import hglib
import os
import re
import logging


REGEX_REPO_NAME = '\/([^/]+)\/*$'
REGEX_REPO_NAME_GROUP = 1


class MercurialRepositoryCloner(IRepositoryCloner):
    """
    Clones mercurial-repositories.
    """
    def __init__(self, settings: dict):
        """
        Creates a new instance of the MercurialRepositoryCloner class.
        :param settings: settings including keys analysis_workspace (path) and repository_folder (folder in
        analysis_workspace)
        """
        self.__settings = settings

    def clone_repositories(self, repository_set: set) -> None:
        # Get path to mercurial repositories.
        directory = self.__settings["analysis_workspace"] + self.__settings["repository_folder"] + "hg/"

        # Create path for mercurial repositories.
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Iterate over every url and clone repositories.
        for url in repository_set:
            # Get repo name
            regex_result = re.search(REGEX_REPO_NAME, url)
            repo_name = regex_result.group(REGEX_REPO_NAME_GROUP)

            # Notify user.
            logging.info("[MercurialRepositoryCloner]: Cloning repository " + repo_name + " from " + url + "...")

            try:
                # Create repo directory.
                repo_directory = directory + repo_name
                if not os.path.exists(repo_directory):
                    os.makedirs(repo_directory)

                # Clone repository.
                hglib.clone(url, repo_directory)
            except hglib.error.CommandError:
                logging.warning("[MercurialRepositoryCloner]: Could not clone repository " + repo_name)

    def clones(self) -> str:
        return "hg"
