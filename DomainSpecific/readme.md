# Domain-specific Knowledge Extraction from CommonCrawl

## Introduction 
Developing data workflows for specific requirements in distributed computing environments can be challenging for data engineers. They often face the following hurdles:

 - Learning to use distributed computing platforms from scratch.
 - Developing data processing modules, even when many are standard and reusable.
 - Constructing data pipelines by assembling these modules into their workflows.

Actually, many of these challenges can be mitigated with a unified framework. To address this, we propose the DataNetwork project. This initiative aims to enable engineers to efficiently meet customized and diverse data requirements using distributed computing resources and shared data storage.

## Getting Started
This section will guide you through setting up and running the DataNetwork framework on your system.
The framework is supported in the following environments. While other operating systems, such as Ubuntu 18.04/22.04 or Windows, are theoretically supported, they have not been tested yet.

1.	Environment
 - [Ubuntu-20.04.1](https://ubuntu.com/download/desktop)
 - [Git-2.41.0](https://git-scm.com/downloads)
 - [Git-lfs-3.4.0](https://git-lfs.com/)
 - [Conda-23.3.1](https://conda.io/projects/conda/en/stable/user-guide/install/download.html)
 - [Python-3.10.14](https://www.python.org/downloads/)
 - Python dependencies in [requirements.txt](requirements.txt) file

2.	Installation

```
# The required libraries will be installed.
pip install -r requirements.txt
```

3.	Usage:

```
# The runtime-dependencies will be installed, and an 'env_ready' file will be generated upon first use.
python submit.py --network_path=${network_path} --run_mode=${run_mode} --computation_path=${computation_path} --storage_path=${storage_path} --docker_path=${docker_path}
``` 

 - network_path: the path of configuration file, which represents the instance of a data network.
 - run_mode: the running mode of data network, it supports Single, MultiProcess, and Batch.
 - computation_path: the path of setting file, which describes the computation resource.
 - storage_path: the path of setting file, which describes the storage resource.
 - docker_path: the path of setting file, which describes the environment resource (ignore it, currently not implemented yet).

4.	Examples:
 - Toy Sample:
```
# Please firstly run this command to ensure the installation is correct.
# If it fails, such as unmatched environment, mannually fix the missing dependencies in the dependency/requirements.txt file.
python submit.py --network_path=./configs/network_template.json --run_mode=Single
```

 - Domain-specific Knowledge Data Extraction from CommonCrawl:
```
# Refer to sample_run.sh script for details.
bash sample_run.sh
```
