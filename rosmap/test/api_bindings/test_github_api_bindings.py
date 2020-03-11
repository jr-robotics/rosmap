import unittest
from rosmap.api_bindings.github_api_bindings import GithubApiBindings

class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.__api_bindings = GithubApiBindings("pichlermarc", "", 5000)

    def test_get_issues_does_not_error(self):
        for issue in self.__api_bindings.get_issues("https://github.com/ros/common_msgs.git", "open"):
            print(issue)

    def test_stargazer_count_does_not_error(self):
        stargazer_count = self.__api_bindings.get_stargazer_count("https://github.com/ros/common_msgs.git")
        print(stargazer_count)

    def test_pull_request_check_correct(self):
        issue = {"pull_request": "test"}
        


if __name__ == '__main__':
    unittest.main()
