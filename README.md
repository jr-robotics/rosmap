# rosmap

## What is this repository for?

This repository contains the implementation of the analysis-tool used in our paper **"Can i depend on you? Mapping the dependency and quality landscape or ROS packages"**, published in the proceedings of the IRC 2019 conference. If you want to cite this repository, please cite the original paper instead:

```
@inproceedings{pichler_can_2019,
    title = {Can i depend on you? {Mapping} the dependency and quality landscape or {ROS} packages},
    booktitle = {Proceedings of the 3rd {International} {Conference} on {Robotic} {Computing}},
    publisher = {IEEE},
    author = {Pichler, Marc and Dieber, Bernhard and Pinzger, Martin},
    month = feb,
    year = {2019}
}
```

The application contained in this repository provides the means to:
  - acquire a set of links to git, mercurial and subversion repositories that are suspected to contain ROS-Packages.
  - acquire local copies of all of these repositories for later analysis.
  - analyze these repositories by extracting the names of the contained ROS-Packages, their dependencies, as well as amount of Github-Stars or Bitbucket-Watchers, counting how many branches and contributors there are, and more information on the popularity of the project.
  
## How do I use it?

### Step 1: Setup
  - Install the prerequisites on your system.
    - On Ubuntu 16.04 run (`sudo apt-get install python3.5 python-pip git subversion mercurial`)
    - **Note: this tool only supports (and has only been tested on) Ubuntu;** if you want to tinker with it on other systems see a [list of prerequisites](#system-prerequisites).
  - Clone this repository.
  - `cd` into the cloned repository.
  - Install requirements.txt (`pip install -r requirements.txt`)

### Step 2: Configuration

  Since this application will use GitHub's API to extract data from it, it is advised to add a GitHub username as well as an API-Token to its config-file. You will find a sample config file at `./config/config.json` inside repository. Much of it is already preconfigured.
  
  
  ```
  {
      "github_username": "USERNAME_HERE",
      "github_password": "API_TOKEN_HERE",
      "github_search_topic": "ros",
      "github_search_rate_limit": 1800,
      "github_api_rate_limit": 5000, 
      .
      .
      .
  }
  ```
  
  Simply replace `USERNAME_HERE` with your account's username, and the `API_TOKEN_HERE` with your API-Token. Alternatively you can also use your password if two-factor authentication is not enabled for your account.
  
  The rate-limits are already preconfigured to the standard rate limits of GitHub's API for authenticated users (5000 requests/hour for the v3 API, configured in `github_api_rate_limit` and 1800 requests/hour for the Search-API, configured in `github_search_rate_limit`). It is also possible to omit authentication, however, the rate-limit will need to be reduced to 60 requests/hour (or 600 requests/hour for search), making analysis of a large amount of repositories practically unfeasible.
  ```
  {
      ...,
      "rosdistro_url": "https://github.com/ros/rosdistro",
      "rosdistro_workspace": "~/.rosdistro_workspace/",
      ...
  }
  ```
  
  `rosdistro_url` will already be set to the URL of the rosdistro repository. `rosdistro_workspace` will be the folder to clone the rosdistro repository into, by default it is at `~/.rosdistro_workspace`.
  
  ```
  {
     ...,
     "bitbucket_repo_page": "https://bitbucket.org/repo/all/",
     "bitbucket_repo_search_string": "ros",
     "bitbucket_api_rate_limit": 1000,
     ...
  }
  ```
  Since Bitbucket does not provide a search API, the code provided in this repository uses their web-interface and extracts the information from the results-pages. The link to this page is defined in `bitbucket_repo_page`.
 
  The search term is set to `ros` by default, and can be changed to any other search term by changing the value of `bitbucket_repo_search_string`.
  
  Bitbucket does not require users to be logged in to use their API, however their rate limit is 1000 requests/hour, which is already preconfigured.
  
  ```
  {
     ...,
     "version_control_systems": ["hg", "git", "svn"],
     "analysis_workspace" : "~/.analysis_workspace/",
     "repository_folder": "repositories/",
     "social_coding_sites": ["bitbucket", "github"],
     "package_xml_dependency_tags": ["build_depend",
                                     "run_depend",
                                     "depend",
                                     "buildtool_depend",
                                     "build_export_depend",
                                     "exec_depend",
                                     "test_depend",
                                     "doc_depend"],
     "manifest_xml_dependency_tags": ["depend"]
  }
  ```
  
  `version_control_systems` provides the possibility to add or remove all repositories of a type form analysis. The available types are `git`, `svn` (Subversion), and `hg` (Mercurial).
  
  `analysis_workspace` will be the directory in which the list of repositories is saved, as well as the place where all repositories will be cloned to. `repository_folder` is the subfolder in `analysis_workspace` that will be used to clone the different repsitories to.
  
  `social_coding_sites` is a list of social coding sites that can be analyzed, `github` and `bitbucket` are currently implemented.
  
  `package_xml_dependency_tags` is the list of tags that are considered a dependency in a `package.xml` file. By default, we scan for every dependency tag that exists, but the list can be modified at will, the content of the tags will show up in the output file as package dependencies.
  
  `manifest_xml_dependency tags` serves the same purpose as `package_xml_dependency_tags`, but for the legacy rosbuild `manifest.xml` files.
  
### Step 3: Running the program
    
You can either run a [full analysis](#step-3a-full-analysis), [skip certain steps](#step-3b-partial-analysis), or run an [analysis just for your repositories](#).
   
#### Step 3.a Full Analysis

   To run a full analysis, either move your config file to the config folder and replace the default `config.json`, or provide it as a parameter to the program.
   
   To perform the full analysis run `./analyze.py --config /path/to/your/config.file --output /path/to/output.file`.
   If you modified or replaced the `./config/config.json`, it will load it automatically, you do not need to provide the `--config` parameter, you can simply run `./analyze.py --output /path/to/output.file` (**NOTE: if the `--output` parameter is not provided, only the parse and download steps will be performed, for running analysis only or skipping steps see [Step 3.b](#step-3b-partial-analysis)**).
   
   A full analysis will include:
   - **gathering repository URLs** from github- and bitbucket-searches as well as the official ROS Index found in the rosdistro-repository. The URLs will be written to your `analysis_workspace`, in the subfolder `links/`. For each type, there will be one file named accordingly. Re-running the analysis will parse all URLs again.
   - **cloning ALL repositories** found while gathering URLs to your machine. **(NOTE: This operation requires a significant amount of disk space, our analysis resulted in over 70GB worth of repositories, make sure you have the space for it in advance.)**
   - **Analyze all repositories** for contained packages, their dependencies, cpplint-issues, github stars (bitbucket watchers), branch count, issue count and duration, last updated time, and contributors.

#### Step 3.b: Partial analysis

You can also skip steps by using these in alone or in combination:
   - `--load_existing`, which will load previously existing repository URLs from the file
   - `--skip_download`, which will skip the cloning process.
   - by omission of `--output ./path/to/output.file`, which will skip the analysis step.
   
#### Step 3.c: Analyze just your local repositories

You can skip the downloading of files, and just use your local repositories for analysis. To do this, you can run `.analysis.py --skip_download --load_existing --output /path/to/your/output.file` after moving your repositories to the repositories folder specified in your configuration file (`<analysis_workspace>/<repository_folder>`).

### Step 4: Inspect output

After running the analysis, the output will be written to your defined output file. The results will follow this JSON-Schema, meaning of the different parts is given in the "title" fields:

```json
{  
   "type":"array",
   "title":"Array that contains all repository-objects.",
   "items":{  
      "type":"object",
      "title":"The repository class.",
      "required":[  
         "url",
         "continuous_integration",
         "rosinstall",
         "contributors",
         "branch_count",
         "changelog",
         "packages",
         "cpplint_errors",
         "last_update",
         "readme"
      ],
      "properties":{  
         "open_issues":{  
            "type":"integer",
            "title":"Number of open issues."
         },
         "url":{  
            "type":"string",
            "title":"The origin-url of the repository"
         },
         "continuous_integration":{  
            "type":"boolean",
            "title":"Is there a file present that suggests continuous integration is set up?"
         },
         "rosinstall":{  
            "type":"boolean",
            "title":"Is there a rosinstall file present?"
         },
         "open_pull_requests":{  
            "type":"integer",
            "title":"Number of open pull-requests"
         },
         "contributors":{  
            "type":"integer",
            "title":"Number of contributors"
         },
         "branch_count":{  
            "type":"integer",
            "title":"Number of branches"
         },
         "changelog":{  
            "type":"boolean",
            "title":"Is there a CHANGELOG file present?"
         },
         "issue_durations":{  
            "type":"array",
            "title":"Issue durations in seconds.",
            "items":{  
               "type":"number"
            }
         },
         "packages":{  
            "type":"array",
            "title":"Packages contained in this repository.",
            "items":{  
               "type":"object",
               "title":"The package-class.",
               "required":[  
                  "name",
                  "dependencies"
               ],
               "properties":{  
                  "name":{  
                     "type":"string",
                     "title":"The package's name"
                  },
                  "dependencies":{  
                     "type":"array",
                     "title":"The package's dependencies (package names of dependencies)",
                     "items":{  
                        "type":"string"
                     }
                  }
               }
            }
         },
         "closed_pull_requests":{  
            "type":"integer",
            "title":"Number of closed pull-requests"
         },
         "stars":{  
            "type":"integer",
            "title":"Number of github-stars/bitbucket-watchers"
         },
         "cpplint_errors":{  
            "type":"integer",
            "title":"Number of cpplint errors."
         },
         "last_update":{  
            "type":"number",
            "title":"Time of last repository commit as UNIX-Timestamp"
         },
         "readme":{  
            "type":"boolean",
            "title":"Is there a readme-file present?"
         }
      }
   }
}
```

## System Prerequisites
  - Python 3.5
  - pip
  - git
  - subversion
  - mercurial
  
## Python Prerequisites
  - GitPython (2.1.8)
  - pyyaml (4.2b1)
  - pyquery (1.4.0)
  - urllib3
  - python-hglib (2.6.1)
  - svn (0.3.46)
  - python-dateutil (2.7.5)
  - cpplint
