#!/usr/bin/env python3
from sys import argv
from os import environ

if __name__ == "__main__":
    if argv[1] == "Username for 'https://github.com': ":
        print(environ['GIT_USERNAME'])
        exit()

    if argv[1] == "Password for 'https://" + environ['GIT_USERNAME'] + "@github.com': ":
        print(environ['GIT_PASSWORD'])
        exit()

    exit(1)