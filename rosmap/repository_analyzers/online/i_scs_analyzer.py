from abc import ABCMeta, abstractmethod


class ISCSRepositoryAnalyzer(object):
    """
    Interface for classes implementing remote analysis of repositories from social coding sites (scs).
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def analyze_repositories(self, repo_details: dict) -> None:
        """
        Analyzes repositories listed in repo_details.
        """
        raise NotImplementedError

    @abstractmethod
    def analyzes(self) -> str:
        """
        Returns which type of remote is analyzed by this analyzer.
        :return: A string designating which type of repository is cloned (e.g. "bitbucket", "github",...)
        """
        raise NotImplementedError
