from .i_repository_cloner import IRepositoryCloner
from git import Repo
from git import GitCommandError
import os
import re
import logging

REGEX_REPO_NAME = '\/([^\/]+?)\/([^\/]+?)\.git'
REGEX_REPO_USER_GROUP = 1
REGEX_REPO_NAME_GROUP = 2


class GitRepositoryCloner(IRepositoryCloner):

    def __init__(self, settings: dict):
        self.__settings = settings

    def clone_repositories(self, repository_set: set) -> None:
        # Create folder
        if not os.path.exists(self.__settings["analysis_workspace"] + self.__settings["repository_folder"] + "git/"):
            os.makedirs(self.__settings["analysis_workspace"] + self.__settings["repository_folder"] + "git/")

        for url in repository_set:
            # Get repo name
            regex_result = re.search(REGEX_REPO_NAME, url)
            repo_name = regex_result.group(REGEX_REPO_NAME_GROUP)
            user_name = regex_result.group(REGEX_REPO_USER_GROUP)

            # Notify user
            logging.info("[GitRepositoryCloner]: Cloning repository " + repo_name + " from " + url + "...")

            # Suffix in case a repo with the same name already exists

            try:
                # Create directory.
                directory = self.__settings["analysis_workspace"] + self.__settings["repository_folder"] + "git/" + user_name + "_" + repo_name
                if not os.path.exists(directory):
                    os.makedirs(directory)

                # Clone into directory.
                Repo.clone_from(url, directory)

            except GitCommandError:
                logging.warning("[GitRepositoryCloner]: Could not clone repository " + repo_name)

    def clones(self) -> str:
        return "git"
