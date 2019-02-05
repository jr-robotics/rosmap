from abc import ABCMeta, abstractmethod


class IRepositoryCloner(object):
    """
    Interface for classes implementing cloning-functionality for different repository-types.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def clone_repositories(self, repository_set: set) -> None:
        """
        Clones repositories from URLs provided by repository set
        :param repository_set: A set containing repository-URLs.
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def clones(self) -> str:
        """
        Returns which type of repository is cloned by this cloner.
        :return: A string designating which type of repository is cloned (e.g. "git", "hg", "svn", ...)
        """
        raise NotImplementedError
