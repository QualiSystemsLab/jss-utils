import csv
import json
import logging
import sys
import time

from lib import cs_helpers


def read_schedules(schedules_file):
    try:
        with open(f'configs/{schedules_file}', 'r') as f:
            schedules = f.readlines()
            schedules = [l.strip() for l in schedules]
    except Exception as e:
        print(f'Cannot read schedules file: "{schedules_file}", Error: {str(e)}')
        sys.exit(0)
    return schedules

def read_config(config_file='configs/default.json'):
    """Reads a json config file
    """
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f'Cannot read config file: "{config_file}", Error: {str(e)}')
        sys.exit(0)
    return config


def get_logger(logging_config, prefix=''):
    """Creates a logger with provided logging config
    """
    logger_name = logging_config.get('logger_name')
    logging_level = logging_config.get('logger_level')
    logging_path = logging_config.get('logger_path')
    logging_format = logging_config.get('logger_format')
    logging_datefmt = logging_config.get('logger_datefmt')

    logger = logging.getLogger(logger_name)
    level = logging_level.upper()
    logger.setLevel(level)

    logging_path = 'c:/temp/logs' if not logging_path else logging_path

    log_file = f'{logging_path}/{prefix}_{logger_name}_{time.strftime("%m%d%y%H%M%S")}.log'

    try:
        f = open(log_file, 'a')
    except Exception as e:
        print(f'Could not open log file: "{log_file}", Error: {str(e)}')
        sys.exit(0)

    fh = logging.StreamHandler(f)
    sh = logging.StreamHandler()

    formatter = logging.Formatter(logging_format, datefmt=logging_datefmt)

    fh.setFormatter(formatter)
    logger.addHandler(fh)

    sh.setFormatter(formatter)
    logger.addHandler(sh)
    logger.info('Logging started...')
    return logger


def create_topology_dict(topology):
    topology_dict = {
        # "id": topology_id,
        "name": topology.get('Name'),
        "inputs": topology.get('Inputs')
    }
    return topology_dict


# Blueprint inputs and test inputs
# Old parameter format: {'ParameterName': 'ParameterValue'}  new parameter format: {'name': 'value'}
def get_test_parameters(parameters):
    input_params = list()
    if parameters:
        for parameter in parameters:
            input_param = dict()
            # input_param['name'] = parameter.get('ParameterName')
            input_param['name'] = 'additional_parameters'
            input_param['value'] = parameter.get('ParameterValue')
            input_params.append(input_param)
    return input_params


def get_blueprint_parameters(parameters, logger):
    input_params = list()
    # Setting some default parameter values if they do not have good values
    for parameter in parameters:
        if parameter.get('Name') == 'EmailGroup' and parameter.get('Value') == None:
            parameter['Value'] = '[Any]'
        # elif parameter.get('Name') == 'EmailGroup' and parameter.get('Value') not in parameter.get('PossibleValues'):
        #     logger.error(f'Value of Email: {parameter.get("Value")} not in Possible Values: {parameter.get("PossibleValues")}')
            parameter['Value'] = '[Any]'
        elif parameter.get('Name') == 'Location' and parameter.get('Value') == None:
            parameter['Value'] = '[Any]'
        # # Replace RLKN with SOLK - this is specific to specific CDS OPS suite "BTAS CDS Health Check Tests - CoSp
        # elif parameter.get('Name') == 'Location' and parameter.get('Value') == 'RKLN':
        #     parameter['Value'] = 'SOLK'
        elif parameter.get('Name') == 'Terminate Setup on Reboot Error' and parameter.get('Value') == None:
            parameter['Value'] = '[Any]'
        elif parameter.get('Name') == 'RebootUE-Order' and parameter.get('Value') == None:
            parameter['Value'] = '[Any]'
        elif parameter.get('Name') == 'Run UE Reboots' and parameter.get('Value') == None:
            parameter['Value'] = 'no'
        elif parameter.get('Value') == None:
            parameter['Value'] = ''
        input_param = dict()
        input_param['name'] = parameter.get('Name')
        input_param['value'] = parameter.get('Value')
        input_params.append(input_param)
    return input_params


def create_tests_dict(tests):
    tests_list = list()
    test_dict = dict()
    for test in tests:
        # test_string = test.get('TestPath').replace('TestShell\\Tests\\Shared\\Robot\\', '').replace('\\', '/') # Todo: works for Dev
        # test_string = test.get('TestPath').replace('TestShell\\Tests\\Shared\\Robots\\', '').replace('\\', '/')
        test_string = test.get('TestPath').replace('TestShell\\Tests\\Shared\\Robot\\', '').replace('\\', '/') # for LAB only
        test_path = '/'.join(test_string.split('/')[1:-1])
        ## Todo: Hardcoded to VZW: vzw-robot; DEV-LAB: dev_lab_robot; STG-LAB: stg_lab_robot; LAB: robot
        # test_id = 'dev_lab_robot/' + '/'.join(test_string.split("/")[1:]) + '.robot'
        # 'staging_lab_robot/ATFReleaseVerification/FailureAnalysis/SuiteException.robot'
        # test_id = 'staging_lab_robot/' + '/'.join(test_string.split("/")[1:]) + '.robot'
        test_id = 'TST_PATH/' + '/'.join(test_string.split("/")[1:]) + '.robot'
        test_id = '/'.join(test_id.split('/')[0:-1] + [test_id.split('/')[-1].replace('_', '-')])  ## Required to replace "_" with "-"
        test_name = f'{test_string.split("/")[-1]}.robot'
        test_name = test_name.replace("_", "-")  ## Required to replace "_" with "-"
        inputs = get_test_parameters(test.get('Parameters'))
        try:
            duration_in_minutes = int(test.get('EstimatedDuration'))
        except:
            duration_in_minutes = 5
        test_dict = {
            'id': test_id,
            'path': test_path,
            'name': test_name,
            'durationInMinutes': duration_in_minutes,
            # Todo: hardcoded to 5
            # 'durationInMinutes': 5,
            'inputs': inputs
        }
        tests_list.append(test_dict)
    return tests_list

def create_tests_dict_from_jss(tests):
    tests_list = list()
    for test in tests:
        inputs = test.get('inputs')
        test_id = test.get('id')
        test_path = test.get('path')
        test_name = test.get('name')
        duration_in_minutes = test.get('durationInMinutes')
        test_dict = {
            'id': test_id,
            'path': test_path,
            'name': test_name,
            'durationInMinutes': duration_in_minutes,
            'inputs': inputs
        }
        tests_list.append(test_dict)
    return tests_list


# Hardcoded for development purpose
def create_test_dict(test_duration_in_minutes=3):
    test_dict = {
        # "id": "vzw-robot/ATF/data/scripts/SimpleInputSleep.robot",
        "id": "dev_vzw_robot/SadanandTest/SadanandTest.robot",
        "path": "ATF/SadanandTest",
        "durationInMinutes": test_duration_in_minutes,
        "inputs": []
    }
    return test_dict


def create_job_dict(logger, cs_api, job, topologies, domain):
    job_name = job.get('Name')
    job_descr = job.get('Description')
    job_duration_time_buffer = int(job.get('DurationTimeBuffer'))
    # job_duration_time_buffer = 0
    blueprint_name = f'{domain} topologies/{job.get("Topology").get("Name")}'
    for topology in topologies:
        if blueprint_name == topology:
            blueprint_name = topology
            break
    else:
        logger.error(f'{blueprint_name} not found in list of topologies')

    if blueprint_name.startswith('/'):
        blueprint_name = blueprint_name[1:]

    blueprint_id = cs_helpers.get_blueprint_id(blueprint_name, cs_api)
    logger.info(f'Blueprint Name: {blueprint_name}, id: {blueprint_id}')
    blueprint_inputs = get_blueprint_parameters(job.get('Topology').get('GlobalInputs'), logger)
    tests = job.get('Tests')
    # test_dict = create_test_dict(tests)
    tests_dict = create_tests_dict(tests)
    # job_exec_servers = job.get('ExecutionServers')
    # job_logging_profile = job.get('LoggingProfile')
    # job_stop_on_fail = job.get('StopOnFail')
    # job_stop_on_error = job.get('StopOnError')
    # job_email_notifications = job.get('EmailNotifications')

    job_dict = {
        "name": job_name,
        "description": job_descr,
        "durationBufferInMinutes": job_duration_time_buffer,
        # Todo: set buffer to 0
        # "durationBufferInMinutes": 0,
        "blueprint": {
            "id": blueprint_id,
            "name": blueprint_name.split('/')[-1],
            "inputs": blueprint_inputs,
            # "inputs": [],
        },
        "tests": tests_dict
    }
    return job_dict


def create_job_dict_from_jss(logger, job, domain):
    job_name = job.get('name')
    job_descr = job.get('description')
    job_duration_time_buffer = int(job.get('durationBufferInMinutes'))

    blueprint_id = job.get('blueprint').get('id')
    blueprint_name = job.get('blueprint').get('name')
    # blueprint_id = '9cdde564-6a9c-4085-9c9f-dad1dcd4f09f'
    # blueprint_name = 'Empty NFVD'
    blueprint_inputs = job.get('blueprint').get('inputs')
    tests = job.get('tests')

    tests_dict = create_tests_dict_from_jss(tests)

    job_dict = {
        "name": job_name,
        "description": job_descr,
        "durationBufferInMinutes": job_duration_time_buffer,
        "blueprint": {
            "id": blueprint_id,
            "name": blueprint_name,
            "inputs": blueprint_inputs,
        },
        "tests": tests_dict
    }
    return job_dict

def create_dup_job_dict_from_jss(logger, job, domain, num):
    # job_name = job.get('name')
    job_descr = job.get('description')
    job_name = f'Job {num}'
    job_descr = f'{job_name} description'
    job_duration_time_buffer = int(job.get('durationBufferInMinutes'))

    blueprint_id = job.get('blueprint').get('id')
    blueprint_name = job.get('blueprint').get('name')
    # blueprint_id = '9cdde564-6a9c-4085-9c9f-dad1dcd4f09f'
    # blueprint_name = 'Empty NFVD'
    blueprint_inputs = job.get('blueprint').get('inputs')
    tests = job.get('tests')

    tests_dict = create_tests_dict_from_jss(tests)

    job_dict = {
        "name": job_name,
        "description": job_descr,
        "durationBufferInMinutes": job_duration_time_buffer,
        "blueprint": {
            "id": blueprint_id,
            "name": blueprint_name,
            "inputs": blueprint_inputs,
        },
        "tests": tests_dict
    }
    return job_dict


def create_suite_dict(logger, cs_api, suite_info, topologies, domain, auto_start=False, cron_trigger=None):
    """Create a dictionary of suites formatted to match creating suites
    """
    suite_name = suite_info.get('SuiteTemplateName')
    # suite_owner = suite_info.get('Owner')
    # Todo: hardcoded ownername
    suite_owner = 'SVC-atf-sa-cs'
    suite_descr = suite_info.get('Description')
    if auto_start:
        if not cron_trigger:
            cron_trigger = '* 1 * * *'

    jobs_details = list()
    for job in suite_info.get('JobsDetails'):
        jobs_details.append(create_job_dict(logger, cs_api, job, topologies, domain))
    # Todo: Try one job only
    # jobs_details.append(create_job_dict(logger, cs_api, suite_info.get('JobsDetails')[0], topologies))

    json_body = {
        "name": suite_name,
        "ownerUsername": suite_owner,
        "description": suite_descr,
        "testTypeName": "Robot – Verizon Gateway",
        "shouldStartAutomatically": auto_start,
        "cronTrigger": cron_trigger,
        "jobs": jobs_details
    }
    return json_body

def create_suite_dict_from_jss_suite(logger, suite_info, domain, suite_name):
    """Create a dictionary of suites formatted to match creating suites
    """
    # Todo: hardcoded ownername
    suite_owner = 'SVC-atf-sa-cs'
    suite_descr = suite_info.get('description')

    jobs_details = list()
    # for job in suite_info.get('jobs'):
    #     jobs_details.append(create_job_dict_from_jss(logger, job, domain))
    job = suite_info.get('jobs')[0]
    for num in range(100):
        jobs_details.append(create_dup_job_dict_from_jss(logger, job, domain, num))

    auto_start = suite_info.get('shouldStartAutomatically')
    cron_trigger = suite_info.get('cronTrigger') or None

    json_body = {
        "name": suite_name,
        "ownerUsername": suite_owner,
        "description": suite_descr,
        "testTypeName": "Robot – Verizon Gateway",
        "shouldStartAutomatically": auto_start,
        "cronTrigger": cron_trigger,
        "jobs": jobs_details
    }
    return json_body


def create_tests_list(out_csv_file, suite_details):
    out_dict = dict()
    suite_name = suite_details.get('SuiteTemplateName')
    out_dict['Suite Name'] = suite_name
    jobs = suite_details.get('JobsDetails')
    for job in jobs:
        job_name = job.get('Name')
        out_dict['Job Name'] = job_name
        for test in job.get('Tests'):
            test_name = test.get('TestPath')
            out_dict['Test Name'] = test_name
            update_csv(out_csv_file, out_dict)


def create_tests_list_with_blueprint(out_csv_file, suite_details):
    out_dict = dict()
    suite_name = suite_details.get('SuiteTemplateName')
    out_dict['Suite Name'] = suite_name
    jobs = suite_details.get('JobsDetails')
    for job in jobs:
        job_name = job.get('Name')
        try:
            blueprint_name = job.get('Topology').get('Name')
        except AttributeError:
            blueprint_name = ''
        out_dict['Job Name'] = job_name
        out_dict['Blueprint Name'] = blueprint_name
        try:
            tests = job.get('Tests')
        except AttributeError:
            tests = []

        for test in tests:
            test_name = test.get('TestPath')
            out_dict['Test Name'] = test_name
            update_csv(out_csv_file, out_dict)


def create_tests_list_with_blueprint_new_js(out_csv_file, suite_details):
    out_dict = dict()
    suite_name = suite_details.get('name')
    out_dict['Suite Name'] = suite_name
    jobs = suite_details.get('jobs')
    for job in jobs:
        job_name = job.get('name')
        try:
            blueprint_name = job.get('blueprint').get('name')
        except AttributeError:
            blueprint_name = ''
        out_dict['Job Name'] = job_name
        out_dict['Blueprint Name'] = blueprint_name
        try:
            tests = job.get('tests')
        except AttributeError:
            tests = []

        for test in tests:
            # test_path = test.get('path')
            test_name = test.get('path') +'/'+ test.get('name')
            out_dict['Test Name'] = test_name
            update_csv(out_csv_file, out_dict)


def update_csv(csv_file, row):
    """
    :param csv_file:
    :param row: dictionary to write as a new row
    :return:
    """
    with open(csv_file, 'a', newline='') as csvfile:
        fieldnames = row.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        print('Writing ' + str(row))
        writer.writerow(row)


def read_csv(csv_file):
    """
    :param csv_file:
    :param row: dictionary to write as a new row
    :return:
    """
    with open(csv_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row)

def convert_schedule(schedule):
    weekdays = schedule.split(',')[1]
    if 'None' in weekdays:
        return None
    weekdays_str = ','.join([str(i) for i, n in enumerate(bin(int(weekdays))[2:][::-1]) if bool(int(n))])
    start_time_hour = schedule.split(',')[-1].split()[-1].split(':')[0]
    start_time_min = schedule.split(',')[-1].split()[-1].split(':')[1]

    return f'{start_time_min} {start_time_hour} * * {weekdays_str}'

# def xyz_dlt():
#     suitename = f"S1J1T10-{i}"
#     jobname = f"Job{i}-01"
#     ##################CRON########################
#     if (i % 2) == 0:
#         cronTrigger = '1/2 * * * *'
#     else:
#         cronTrigger = '*/2 * * * *'
#     ##################VARS########################
#     ownerUsername = "atf-sa-cs"
#     testDurationInMinutes = 3
#     sleepTime = "--variable sleepTime:90"
#     ##############################################
#     jsonbody = {"name": suitename, "ownerUsername": ownerUsername, "description": "",
#                 "testTypeName": "Robot � Verizon Gateway",
#                 "shouldStartAutomatically": True, "cronTrigger": cronTrigger,
#                 "jobs": [{"name": jobname, "description": "", "durationBufferInMinutes": 0,
#                           "blueprint": {"id": "d90e8aa7-1dcc-43c3-93f2-2b79a970f6cd", "name": "SuiteJobTest",
#                                         "inputs": [{"name": "Run UE Reboots", "value": "no"},
#                                                    {"name": "Terminate Setup on Reboot or Initialize Error",
#                                                     "value": "no"},
#                                                    {"name": "EmailGroup", "value": "None"},
#                                                    {"name": "Initialize ALL PM UEs", "value": "no"},
#                                                    {"name": "Location", "value": "[Any]"}]},
#                           "tests": [{"id": "vzw-robot/ATF/data/scripts/SimpleInputSleep.robot",
#                                      "path": "ATF/data/scripts",
#                                      "durationInMinutes": testDurationInMinutes,
#                                      "inputs": [{"name": "additional_parameters", "value": sleepTime}]},
#                                     ]}]}
#
#     strbody = json.dumps(jsonbody)
#     print(strbody)
#     response = session.request("POST", url, body=strbody, headers=headersdic, preload_content=False, timeout=10)
#
# def update_tst_path(suite_json, env):
#     tst_path = env_tp_mapping.get(env.upper())
#     for job_num, job in enumerate(suite_json.get('jobs')):
#         for tst_num, tst in enumerate(job.get('tests')):
#             # tst[id] = tst.get('id').replace('TST_PATH', tst_path)
#             suite_json.get('jobs')[job_num].get('tests')[tst_num]['id'] = tst.get('id').replace('TST_PATH', tst_path)
#     return suite_json
#
# def update_global_input(suite_json, env, gi_name):
#     old_gi_value = env_gi_mapping.get(env.upper).get(gi_name)[0]
#     new_gi_value = env_gi_mapping.get(env.upper).get(gi_name)[1]
#     for job_num, job in enumerate(suite_json.get('jobs')):
#         for gi_num, gi in enumerate(job.get('Topology').get('GlobalInputs')):
#             if suite_json.get('jobs')[job_num].get('Topology').get('GlobalInputs')[gi_num]['Parameter Name'] == gi_name:
#                 suite_json.get('jobs')[job_num].get('Topology').get('GlobalInputs')[gi_num]['Parameter Value'] = new_gi_value
#     return suite_json

if __name__ == '__main__':
    r = 3
    my_dict = {
        'Suite Name': f'Suite {r}',
        'Job Name': f'Job {r}',
        'Test Name': f'Test {r}'
    }
    update_csv('c:/temp/tst_file.csv', my_dict)
    read_csv('c:/temp/tst_file.csv')

