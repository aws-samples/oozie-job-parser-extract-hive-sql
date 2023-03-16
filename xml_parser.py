import defusedxml.ElementTree as ET
#import xml.etree.ElementTree as ET
import re
import os
import sqlparse
import json
import argparse
from jproperties import Properties
from string import Template
from configparser import ConfigParser


def split_sqls(folder: str, job_name: str, action_name: str, sql_file_name: str, output_folder: str):
    # remove_pattern = re.compile(r"^(--)*set.*", re.IGNORECASE + re.MULTILINE)
    remove_pattern = re.compile(r"^(--|set|add\s+jar).*", re.IGNORECASE + re.MULTILINE)
    orc_pattern = re.compile(r"STORED\s+AS\s+ORC\s*", re.IGNORECASE)
    sql = open(folder + sql_file_name, 'r').read()
    sql_base_path = job_name + "/" + action_name
    script_folder_name = os.sep.join([output_folder, sql_base_path])
    sqls_text = remove_pattern.sub("", sql)
    sql_file_names = []
    for seq, sql in enumerate(sqlparse.split(sqls_text), start=1):
        if not os.path.isdir(script_folder_name):
            os.makedirs(script_folder_name, exist_ok=True)
        sql_file_name = str(seq * 5) + ".sql"
        with open(script_folder_name + "/" + sql_file_name, "w") as sql_file:
            modified_sql = sql.strip().replace("/hive/warehouse/", "s3://${s3_bucket}/data/vpc/")
            modified_sql = orc_pattern.sub("STORED AS PARQUET\n", modified_sql)
            sql_file.write(modified_sql)
        sql_file_names.append((seq * 5, sql_file_name))
    return sql_file_names


def get_co_ordination_parameters(folder: str, co_ord_namespaces: dict) -> dict:
    coord_parser = ET.parse(folder + "coordinator.xml")
    properties = coord_parser.iterfind("./ns0:action/ns0:workflow/ns0:configuration/ns0:property",
                                       namespaces=co_ord_namespaces)
    return dict(map(lambda x: (x[0].text, x[1].text), properties))


def get_job_properties(folder: str, prop_file_name: str):
    job_config = Properties()
    with open(folder + prop_file_name, 'rb') as job_property_file:
        job_config.load(job_property_file)

    return {key: value.data for key, value in job_config.items()}


def generate_scripts(folder: str, namespaces: dict, output_folder: str, job_properties: dict,
                     coordination_parameters: dict, job_name: str):
    parser = ET.parse(folder + "workflow.xml")
    script_details = []

    for action in parser.getroot().findall('ns0:action', namespaces=namespaces):
        hive_steps = action.findall("ns1:hive", namespaces=namespaces)
        action_name = action.get("name")
        for hive_step in hive_steps:
            if hive_step is not None:
                script_name = hive_step.find("ns1:script",
                                             namespaces=namespaces).text
                params = map(
                    lambda x: tuple(x.text.replace("$", "").replace("{", "").replace("}", "").split("=")[::-1]),
                    hive_step.findall("./ns1:param", namespaces=namespaces))
                script_params = list(params)
                sql_base_path = job_name + "/" + action_name
                job_params = {}
                for ele in script_params:
                    try:
                        value = coordination_parameters.get(ele[0]) if coordination_parameters.get(ele[0],
                                                                                                   None) else job_properties.get(
                            ele[0])
                        job_params[ele[1]] = value
                    except Exception:
                        print(ele, "exception")
                file_names = split_sqls(folder=folder, job_name=job_name,
                                        action_name=action_name, sql_file_name=script_name, output_folder=output_folder)
                sql_info = [
                    {"sql_load_order": sql_details[0], "sql_parameters": job_params, "sql_active_flag": "Y",
                     "sql_path": sql_details[1]} for sql_details in file_names]

                script_dict = dict()
                script_dict['name'] = script_name
                script_dict['step_name'] = action_name
                script_dict['sql_info'] = sql_info
                script_dict['id'] = "emr_config"
                script_dict['step_id'] = job_name + "#" + action_name
                script_dict['sql_base_path'] = sql_base_path + "/"
                script_dict['spark_config'] = {
                    "spark.sql.parser.quotedRegexColumnNames": "true"
                }
                json_file_name = os.sep.join(
                        [output_folder, job_name, action_name, action_name + ".json"]), "w"
                print(json_file_name)
                with open(os.sep.join(
                        [output_folder, job_name, action_name, action_name + ".json"]), "w") as dynamo_json:
                    dynamo_json.write(json.dumps(script_dict))
                script_details.append(script_dict)


def parse_job(base_folder: str, job_name: str, version_number: str, hive_action_version: str, coordinator_version: str,
              workflow_version: str, properties_file_name: str):
    perforce_root_folder = base_folder + "perforce/"
    development_folder = base_folder + "development"
    perforce_folder = perforce_root_folder + f"{job_name}/{version_number}/"
    coord_namespaces = {"ns0": f"uri:oozie:coordinator:{coordinator_version}"}
    workflow_namespaces = {"ns0": f"uri:oozie:workflow:{workflow_version}",
                           "ns1": f"uri:oozie:hive-action:{hive_action_version}"}
    coord_params = get_co_ordination_parameters(perforce_folder, coord_namespaces)
    job_properties = get_job_properties(perforce_folder, prop_file_name=properties_file_name)
    print(job_properties)
    generate_scripts(folder=perforce_folder, namespaces=workflow_namespaces, output_folder=development_folder,
                     job_properties=job_properties, coordination_parameters=coord_params, job_name=job_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Oozie job conversion")
    parser.add_argument("--base-folder", required=True, type=str, dest="base_folder", help = "Folder which where the source code is downloaded locally.")
    parser.add_argument("--job-name", required=True, type=str, dest="job_name",
                        help="job_name which needs to be converted")
    parser.add_argument("--job-version", required=True, type=str, dest="job_version",
                        help="Version number based on perforce location where the latest code is")
    parser.add_argument("--hive-action-version", required=True, type=str, dest="hive_action_version",
                        help="Hive action version number from the xml")
    parser.add_argument("--coordinator-action-version", required=True, type=str, dest="coordinator_action_version",
                        help="coordinator version number from the xml")
    parser.add_argument("--workflow-version", required=False, nargs = '?', type=str, dest="workflow_version",
                        help="workflow version number from the xml", default="0.4")
    parser.add_argument("--properties-file-name", required=False, nargs = '?' , type=str, dest="properties_file_name",
                        help="properties file name for the job", default="job.coordinator.properties")
    args = parser.parse_args()

    parse_job(
        base_folder=args.base_folder,
        job_name=args.job_name, version_number=args.job_version, hive_action_version=args.hive_action_version,
        coordinator_version=args.coordinator_action_version, workflow_version=args.workflow_version,
        properties_file_name=args.properties_file_name)

