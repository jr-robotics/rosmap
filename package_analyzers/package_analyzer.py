from abc import ABCMeta, abstractmethod
import os


class PackageAnalyzer(object):
    """
    Abstract base class for plug-ins seeking to implement package analysis.
    """
    __metaclass__ = ABCMeta

    def __init__(self, settings):
        """
        Creates a new instance of a package-analyzer class.
        :param settings: settings containing information for the plug-ins.
        """
        self._settings = settings

    def add_dependency(self, dependant: str, dependency: str, packages: dict) -> None:
        """
        Adds a dependency
        :param dependant: The package that depends on the dependency
        :param dependency: The package that the dependant is dependent on.
        :param packages: The packages and depdendencies of this repository (key: package, value: list of dependencies).
        :return: None
        """
        if not dependant in packages:
            packages[dependant] = dict()
        if not "dependencies" in packages[dependant]:
            packages[dependant]["dependencies"] = list()
        packages[dependant]["name"] = dependant
        packages[dependant]["dependencies"].append(dependency)

    @abstractmethod
    def _analyze(self, path: str) -> dict:
        """
        Analyze the current path for packages (recursively)
        :param path: Path to the repository that possibly contains files.
        :return: Dictionary with package-names and dependencies.
        """
        raise NotImplementedError

    def analyze(self, path: str) -> list:
        return list(self._analyze(path).values())

    def search_files(self, path: str, pattern: str) -> list:
        """
        Searches for files recursively in the file system matching the provided pattern.
        :param path: The path to search in.
        :param pattern: The pattern to search for.
        :return: A list of paths to the found files.
        """
        filellist = []
        for root, dirs, files in os.walk(path):
            for name in files:
                if name.endswith(pattern):
                    filellist.append(os.path.join(root,str(pattern)))
        return filellist