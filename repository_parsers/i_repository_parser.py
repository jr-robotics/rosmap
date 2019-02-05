from abc import ABCMeta, abstractmethod


class IRepositoryParser(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def parse_repositories(self, repository_dict: dict) -> None:
        """
        Parses repository URLs and adds them to the dictionary.
        :param repository_dict: The dictionary to add the repository URLs to (key: repo-type, value: repo-url)
        :return: None
        """

        raise NotImplementedError
