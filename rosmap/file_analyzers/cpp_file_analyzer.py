from .i_file_analyzer import IFileAnalyzer
import subprocess


class CppFileAnalyzer(IFileAnalyzer):
    """Analyzes C++ source and header files."""
    def initialize_fields(self, repo_detail: dict) -> None:
        try:
            repo_detail["cpplint_errors"]
        except KeyError:
            repo_detail["cpplint_errors"] = 0

    def __analyze_file(self, path: str, repo_detail: dict) -> None:
        try:
            cpplint_report = str(subprocess.check_output(
            "cpplint --filter=-whitespace/tab,-whitespace/braces,-build/headerguard,-readability/streams,-build/include_order,-whitespace/newline,-whitespace/labels,-runtime/references " + path,
            shell=True, stderr=subprocess.STDOUT))
            if "Total errors found:" in cpplint_report:
                repo_detail["cpplint_errors"] += int(cpplint_report.split('\n')[-2].split(': ')[-1])
        except subprocess.CalledProcessError as error:
            cpplint_report = error.output
            repo_detail["cpplint_errors"] += int(cpplint_report.decode("utf-8").split('\n')[-2].split(': ')[-1])

    def analyze_files(self, path_list: list, repo_detail: dict):
        for file_path in filter(lambda k: k.endswith(".hpp") or k.endswith(".cpp") or k.endswith(".h"), path_list):
            self.__analyze_file(file_path, repo_detail)



