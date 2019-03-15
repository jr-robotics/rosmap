from abc import ABCMeta, abstractmethod


class IRepositoryAnalyzer(object):
    """
    Interface for classes implementing Repository-analysis.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def analyze_repositories(self, path: str, repo_details: dict) -> None:
        """
        Analyzes all repositories directly under the root of the given path (does not recurse).
        :param path: Path to the repositories.
        :param repo_details: Details about the repositories.
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def analyzes(self) -> str:
        raise NotImplementedError
