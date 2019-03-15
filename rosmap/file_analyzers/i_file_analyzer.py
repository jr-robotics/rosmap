from abc import ABCMeta, abstractmethod


class IFileAnalyzer(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def initialize_fields(self, repo_detail: dict) -> None:
        """
        Initialize fields on repo_detail needed for analysis of this file-type.
        :param repo_detail:
        :return:
        """
        raise NotImplementedError

    def analyze_files(self, path_list, repo_detail: dict):
        raise NotImplementedError
