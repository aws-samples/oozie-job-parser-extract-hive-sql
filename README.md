## Prerequisites:
Below packages are needed for parsing the SQL's and reading the Oozie properties file

- sqlparse==0.4.2
- jproperties==2.1.1


## Setup:
- Install Python3
- Create a virtual environment 
```shell
	python3 -m venv /path/to/new/virtual/environment
```
- Activate newly created virtual environment
```shell
	source /path/to/new/virtual/environment/bin/activate
```
- Git clone the project
```shell
	git clone https://github.com/aws-samples/oozie-job-parser-extract-hive-sql
```
- Install dependent packages
```shell
	cd oozie-job-parser-extract-hive-sql
	pip install -r requirements.txt
```
## Usage:

usage: xml_parser.py [-h] --base-folder BASE_FOLDER --job-name JOB_NAME
                     --job-version JOB_VERSION --hive-action-version
                     HIVE_ACTION_VERSION --coordinator-action-version
                     COORDINATOR_ACTION_VERSION
                     [--workflow-version [WORKFLOW_VERSION]]
                     [--properties-file-name [PROPERTIES_FILE_NAME]]
xml_parser.py: error: the following arguments are required: --base-folder, --job-name, --job-version, --hive-action-version, --coordinator-action-version


## Sample command:
```shell
	python xml_parser.py --base-folder ./sample_jobs/ --job-name sample_oozie_job_name --job-version V3 --hive-action-version 0.4 --coordinator-action-version 0.4 --workflow-version 0.4 --properties-file-name job.coordinator.properties
```
