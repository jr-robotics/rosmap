from .package_analyzer import PackageAnalyzer
from xml.etree.cElementTree import parse
from xml.etree.cElementTree import ParseError
import logging

class PackageXmlAnalyzer(PackageAnalyzer):
    """
    Analyzer plug-in for ROS' package.xml files (catkin).
    """

    def analyze_file(self, path: str, dependencies: dict) -> dict:
        # Parse xml
        try:
            file = open(path, "r")
            tree = parse(file)
        except ParseError:
            logging.warning("[PackageXmlAnalyzer]: Could not parse " + path + "; omitting file.")
            return dependencies

        element = tree.getroot()
        packagename = element.find('name').text

        for tag in self._settings["package_xml_dependency_tags"]:
            for element in element.findall(tag):
                self.add_dependency(packagename, element.text, dependencies)

    def _analyze(self, path: str) -> dict:

        packages = dict()
        filellist = self.search_files(path, "package.xml")

        for filename in filellist:
            logging.info("[PackageXmlAnalyzer]: Analyzing " + filename)
            self.analyze_file(filename, packages)

        return packages


