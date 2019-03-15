#!/usr/bin/env python3

from setuptools import setup, find_packages
setup(
    name="rosmap",
    version="0.1",
    packages=find_packages(),
    scripts=['analyze.py'],
    install_requires=['GitPython>=2.1.8',
                      'pyyaml>=4.2b1',
                      'pyquery>=1.4.0',
                      'urllib3',
                      'python-hglib>=2.6.1',
                      'svn>=0.3.46',
                      'python-dateutil>=2.7.5',
                      'cpplint'],
    package_data={'':'config/config.json'},
    author="Marc Pichler",
    author_email="marc.pichler@joanneum.at",
    license="MIT",
    description="Clones and analyzes ROS-Packages.",
    url="https://github.com/jr-robotics/rosmap",
    project_urls={
        "Source Code": "https://github.com/jr-robotics/rosmap"
    },
    python_requires='~=3.5',
)
