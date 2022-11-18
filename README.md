## Prerequisites:
Below packages are needed for parsing the SQL's and reading the Oozie properties file

- sqlparse==0.4.2
- jproperties==2.1.1

## Usage:

usage: xml_parser.py [-h] --base-folder BASE_FOLDER --job-name JOB_NAME
                     --job-version JOB_VERSION --hive-action-version
                     HIVE_ACTION_VERSION --coordinator-action-version
                     COORDINATOR_ACTION_VERSION
                     [--workflow-version [WORKFLOW_VERSION]]
                     [--properties-file-name [PROPERTIES_FILE_NAME]]
xml_parser.py: error: the following arguments are required: --base-folder, --job-name, --job-version, --hive-action-version, --coordinator-action-version

## Sample command:

python oozie_xml_parser.py --base-folder /Users/username/ --job-name sample_oozie_job_name --job-version V3 --hive-action-version 0.2 --coordinator-action-version 0.4 --workflow-version 0.5 --properties-file-name job.coordinator.properties
