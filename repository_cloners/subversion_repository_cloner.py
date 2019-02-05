from .i_repository_cloner import IRepositoryCloner
import os
import svn.remote
import svn.exception
import urllib3
import logging


class SubversionRepositoryCloner(IRepositoryCloner):

    def __init__(self, settings: dict):
        """
        Creates a new instance of the SubversionRepositoryCloner-class.
        :param settings: settings including keys analysis_workspace (path) and repository_folder (folder in
        analysis_workspace)
        """
        self.__settings = settings

    def clone_repositories(self, repository_set: set) -> None:
        # Create folder
        directory = self.__settings["analysis_workspace"] + self.__settings["repository_folder"] + "svn/"
        if not os.path.exists(directory):
            os.makedirs(directory)

        for url in repository_set:
            # Generate folder-name
            repo_name = url.replace("/", "_")

            # Notify user.
            logging.info("[SubversionRepositoryCloner]: Cloning repository " + repo_name + " from " + url + "...")

            repo_directory = directory + repo_name
            http = urllib3.PoolManager()

            try:
                # Make sure server and path still exist.
                status = http.request('GET', url, timeout=2).status
                if status == 200:
                    try:
                        # Create repo directory.
                        if not os.path.exists(repo_directory):
                            os.makedirs(repo_directory)

                        # Check out SVN repository.
                        svn.remote.RemoteClient(url).checkout(repo_directory)
                    except svn.exception.SvnException:
                        logging.warning("[SubversionRepositoryCloner]: Could not clone from " + url)
                else:
                    logging.warning("[SubversionRepositoryCloner]: Could not clone from "
                                 + url + ", server responded with " + str(status))
            except urllib3.exceptions.MaxRetryError:
                logging.warning("[SubversionRepositoryCloner]: Could not reach " + url + ", connection timeout...")

    def clones(self) -> str:
        return "svn"
