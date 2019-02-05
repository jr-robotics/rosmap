import yaml
import os
import git
import logging
from .i_repository_parser import IRepositoryParser


class RosdistroRepositoryParser(IRepositoryParser):
    """
    Pulls the rosdistro-package and gets all urls from the rosdistro files.
    """

    def __init__(self, settings: dict):
        """
        Creates a new instance of the RosdistroRepositoryParser class
        :param settings: Settings containing information about rosdistro_workspace and rosdistro_url
        """
        self.__settings = settings

    def __get_rosdistro_repository(self) -> None:
        """
        Clones the repository from rosdistro_url into rosdistro_workspace (defined in settings)
        :return: None
        """
        if not os.path.exists(self.__settings["rosdistro_workspace"]):
            os.makedirs(self.__settings["rosdistro_workspace"])
        try:
            logging.info("[RosdistroRepositoryParser]: Cloning rosdistro repository...")
            git.Repo.clone_from(self.__settings["rosdistro_url"], self.__settings["rosdistro_workspace"])
        except git.exc.GitCommandError:
            logging.warning("[RosdistroRepositoryParser]: Repository already exists, pulling changes...")
            repo = git.Repo(self.__settings["rosdistro_workspace"])
            repo.remotes.origin.pull()
        logging.info("[RosdistroRepositoryParser]: Rosdistro up-to-date...")

    def __get_urls_from_file(self, file_path: str, repository_dict: dict) -> None:
        """
        Gets the URLs from a distribution.yaml that adheres to rosdistro-specs.
        :param file_path: path to a distribution.yaml file
        :param repository_dict: dictionary with repository-type (git, svn, hg, ...) as key and the repo-url as value
        :return: None
        """

        # Load file.
        file = open(file_path, 'r')
        rosdistro = yaml.load(file)

        # Iterate repositories and add them to the repository_dict.
        for repository in rosdistro["repositories"]:
            try:
                vcs_type = str(rosdistro["repositories"][repository]["doc"]["type"])
                url = str(rosdistro["repositories"][repository]["doc"]["url"])
                repository_dict[vcs_type].add(url)
            except KeyError:
                pass

            try:
                vcs_type = str(rosdistro["repositories"][repository]["doc"]["type"])
                url = str(rosdistro["repositories"][repository]["source"]["url"])
                repository_dict[vcs_type].add(url)
            except KeyError:
                pass

            try:
                # This has to be a git repository (required by bloom)
                repository_dict["git"].add(rosdistro["repositories"][repository]["release"]["url"])
            except KeyError:
                pass

    def parse_repositories(self, repository_dict: dict) -> None:
        # Actually get the repository
        self.__get_rosdistro_repository()

        # Parse index.yaml
        index_file = open(self.__settings["rosdistro_workspace"] + "index.yaml", "r")
        index_yaml = yaml.load(index_file)

        # Get all urls from all distribution.yaml files
        for distribution in index_yaml["distributions"]:
            logging.info("Parsing distribution " + index_yaml["distributions"][distribution]["distribution"][0])
            self.__get_urls_from_file(self.__settings["rosdistro_workspace"]
                                      + index_yaml["distributions"][distribution]["distribution"][0],
                                      repository_dict)