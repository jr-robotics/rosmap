from .i_file_analyzer import IFileAnalyzer


class ExistenceFileAnalyzer(IFileAnalyzer):
    """
    Checks if files exist, and saves true or false to the repo_detail.
    """

    def analyze_files(self, path_list, repo_detail: dict):
        for path in path_list:
            self.__analyze_file(path, repo_detail)

    def __analyze_file(self, path: str, repo_details: dict) -> None:
        file = path.split("/")[-1]
        repo_details["readme"] = repo_details["readme"] or "readme" in file.lower()
        repo_details["changelog"] = repo_details["changelog"] or "changelog" in file.lower()
        repo_details["continuous_integration"] = repo_details["continuous_integration"] or \
                                                              ".travis.yml" in file.lower() \
                                                              or ".gitlab-ci.yml" in file.lower() \
                                                              or "bitbucket-pipelines" in file.lower()
        repo_details["rosinstall"] = repo_details["rosinstall"] or ".rosinstall" in file.lower()

    def initialize_fields(self, repo_detail: dict) -> None:
        details = ["readme", "changelog", "continuous_integration", "rosinstall"]
        for detail in details:
            try:
                repo_detail[detail]
            except KeyError:
                repo_detail[detail] = False
