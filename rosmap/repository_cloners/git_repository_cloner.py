from .i_repository_cloner import IRepositoryCloner
from git import Repo
from git import GitCommandError
import os
import re
import logging
from shutil import copy

REGEX_REPO_NAME = '\/([^\/]+?)\/([^\/]+?)\.git'
REGEX_REPO_USER_GROUP = 1
REGEX_REPO_NAME_GROUP = 2


class GitRepositoryCloner(IRepositoryCloner):

    def __init__(self, settings: dict):
        self.__settings = settings

    def clone_repositories(self, repository_set: set) -> None:
        copy(os.path.dirname(os.path.realpath(__file__)) + "/git_askpass.py", self.__settings["analysis_workspace"])
        os.chmod(self.__settings["analysis_workspace"] + "/git_askpass.py", 0o777)
        os.environ['GIT_ASKPASS'] = self.__settings["analysis_workspace"] + "/git_askpass.py"
        print(os.environ['GIT_ASKPASS'])
        os.environ['GIT_USERNAME'] = self.__settings["github_username"]
        os.environ['GIT_PASSWORD'] = self.__settings["github_password"]
        # Create folder
        if not os.path.exists(self.__settings["analysis_workspace"] + self.__settings["repository_folder"] + "git/"):
            os.makedirs(self.__settings["analysis_workspace"] + self.__settings["repository_folder"] + "git/")

        for url in repository_set:
            # Get repo name

            regex_result = re.search(REGEX_REPO_NAME, url)
            if regex_result is not None:
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
