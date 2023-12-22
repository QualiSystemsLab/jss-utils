from QualiJSSAPI import QualiJSSAPI
from cs_helpers import get_all_domains, get_api
from helpers import read_config, get_logger

def get_running_suites(domain, jss_api):
  suites = jss_api.get_all_suites(domain)
  suite_executions = list()
  suite_status = 'Running'
  
  for suites in suites:
    suite_name = suite.get('name')
	if 'adhoc' in suite_name.lower():
      continue
    suite_id = suite.get('id')
    suite_execution_details = jss_api.get_suite_executions(domain, suite_id)
    sute_executions += [{'Domain': domain, 'SuiteName': suite_name, 'SuiteId': suite_id}
                         for suite_execution in suite_execution_details
                         if suite_execution.get('statusDescription') == suite_status]
                         
    return suite_executions
    

def stop_suites(domain, jss_api, suites, suite_id):
  for suite_id in suites:
    jss_api.stop_suite_execution(logger, domain, suite_id)
    
if __name__ == '__main__':
  domain_name = 'robot'
  
  config_file = 'C:/Utils/Configs/lab.json'
  logger_config_file = 'C:/Utils/Configs/logger_config.json'
  
  config = read_config(config_file)
  logger_config = read_config(logger_config_file)
  
  config['Domain'] = domain_name
  jss_api = QualiJSSAPI(config)
  logger = get_logger(logger_config, domain_name)
  
  running_suites = get_running_suites(domain_name, jss_api)
  
  print(running_suites)
  
  
