#!/usr/bin/env python3
import argparse
import json
import os
import logging
from rosmap.loaders.module_loader import ModuleLoader
from shutil import copy

PROGRAM_DESCRIPTION = ""


def load_parsers(settings: dict) -> list:
    return ModuleLoader.load_modules(os.path.dirname(os.path.realpath(__file__)),
                                        "repository_parsers",
                                        ["IRepositoryParser"],
                                        "RepositoryParser",
                                        settings)


def load_cloners(settings: dict) -> dict:
    cloners = dict()
    for cloner in ModuleLoader.load_modules(os.path.dirname(os.path.realpath(__file__)),
                                            "repository_cloners",
                                            ["IRepositoryCloner"],
                                            "RepositoryCloner",
                                            settings):
        cloners[cloner.clones()] = cloner
    return cloners


def load_package_analyzers(settings: dict) -> list:
    return ModuleLoader.load_modules(os.path.dirname(os.path.realpath(__file__)),
                                              "package_analyzers",
                                              ["PackageAnalyzer"],
                                              "Analyzer",
                                              settings)


def load_file_analyzers() -> list:
    return ModuleLoader.load_modules(os.path.dirname(os.path.realpath(__file__)),
                                 "file_analyzers",
                                 ["IFileAnalyzer"],
                                 "FileAnalyzer")


def load_analyzers(settings: dict) -> dict:
    analyzers = dict()
    for analyzer in ModuleLoader.load_modules(os.path.dirname(os.path.realpath(__file__)),
                                              "rosmap/repository_analyzers/offline",
                                              ["IRepositoryAnalyzer", "AbstractRepositoryAnalyzer"],
                                              "RepositoryAnalyzer",
                                              load_package_analyzers(settings),
                                              load_file_analyzers()):
        analyzers[analyzer.analyzes()] = analyzer
    return analyzers


def load_remote_analyzers(settings: dict) -> dict:
    remote_analyzers = dict()
    for analyzer in ModuleLoader.load_modules(os.path.dirname(os.path.realpath(__file__)),
                                              "rosmap/repository_analyzers/online",
                                              ["ISCSRepositoryAnalyzer"],
                                              "RepositoryAnalyzer",
                                              settings):
        remote_analyzers[analyzer.analyzes()] = analyzer
    return remote_analyzers


def write_to_file(path, repo_details):
    output_file = open(path, "w")
    output_file.write(json.dumps(list(repo_details.values())))
    output_file.close()


def main():
    # Create argument-parser
    parser = argparse.ArgumentParser(description=PROGRAM_DESCRIPTION)
    parser.add_argument("--config", "-c", help="Add a path to the config.json file that contains, usernames, api-tokens and settings.", default=os.path.dirname(os.path.realpath(__file__)) + "/config/config.json")
    parser.add_argument("--load_existing", "-l", help="Use this flag to load previous link-files from workspace.", default=False, action="store_true")
    parser.add_argument("--skip_download", "-d", help="Use this flag to skip downloading of repositories to your workspace.", default=False, action="store_true")
    parser.add_argument("--output", "-o", help="Add a path to the output file for the analysis. If this path is not defined, analysis will not be performed. ", default="")
    parser.add_argument("--generate_config", help="Generates a config file on the given path.")

    # Parse arguments
    arguments = parser.parse_args()

    # Set up logger
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    if arguments.generate_config is not None:
        copy(os.path.dirname(os.path.realpath(__file__)) + "/config/config.json", arguments.generate_config)
        return 0

    # Warn user that output has to be set to analyze:
    if arguments.output == "":
        logging.warning("parameter --output has not been defined, analysis will be skipped, add --output <path> to perform analysis.")

    # Load settings.
    configfile = open(arguments.config, "r")
    settings = json.loads(configfile.read())

    # Expand home directories.
    settings["analysis_workspace"] = os.path.expanduser(settings["analysis_workspace"])
    settings["rosdistro_workspace"] = os.path.expanduser(settings["rosdistro_workspace"])

    # Initialize dictionaries.
    repositories = dict()
    for vcs in settings["version_control_systems"]:
        repositories[vcs] = set()

    if not arguments.load_existing:
        # Parse repositories
        logging.info("[Parser]: Parsing repositories...")
        parsers = load_parsers(settings)
        for parser in parsers:
            parser.parse_repositories(repositories)

        # Create folder
        if not os.path.exists(settings["analysis_workspace"]):
            os.makedirs(settings["analysis_workspace"]+"links/")

        # Write to file.
        logging.info("[Parser]: Writing repository links to file...")
        for vcs, repository_set in repositories.items():
            logging.info("[Parser]: Writing file for " + vcs)
            with open(settings["analysis_workspace"]+"links/" + vcs, "w+") as output_file:
                for repository in repository_set:
                    output_file.write(repository + "\n")
    else:
        for vcs in settings["version_control_systems"]:
            with open(settings["analysis_workspace"]+"links/" + vcs, "r") as output_file:
                for line in output_file:
                    repositories[vcs].add(line.rstrip("\r\n"))

    if not arguments.skip_download:
        cloners = load_cloners(settings)

        logging.info("[Cloner]: Cloning repositories...")

        for vcs in settings["version_control_systems"]:
            if vcs in cloners:
                cloners[vcs].clone_repositories(repositories[vcs])
            else:
                logging.warning("[Cloner]: Cannot clone repositories of type " + vcs + ": No cloner found for this type...")

    if not arguments.output == "":
        analyzers = load_analyzers(settings)
        repo_details = dict()
        for vcs in settings["version_control_systems"]:
            if vcs in analyzers:
                analyzers[vcs].analyze_repositories(settings["analysis_workspace"] + settings["repository_folder"] + vcs,
                                                    repo_details)
            else:
                logging.warning("Cannot analyze repositories of type " + vcs + ": No analyzer found for this type...")

        write_to_file(arguments.output, repo_details)

        remote_analyzers = load_remote_analyzers(settings)
        for scs in settings["social_coding_sites"]:
            if scs in remote_analyzers:
                remote_analyzers[scs].analyze_repositories(repo_details)
            else:
                logging.warning("Cannot analyze scs of type " + scs + ": No analyzer found for this type...")

        write_to_file(arguments.output, repo_details)

    logging.info("Actions finished. Exiting.")





