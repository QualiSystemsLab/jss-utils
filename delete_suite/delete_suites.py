import helpers
from lib.QualiJSSAPI import QualiJSSAPI
import cloudshell.helpers.scripts.cloudshell_scripts_helpers as cs_helpers

from cloudshell.api.cloudshell_api import AttributeNameValue


def main(environment, domain, logger, suites_names=None):
    config_file = f'C:/Configs/{environment}.json'
    quali_jss_config = helpers.read_config(config_file)
    jss_domain = domain
    quali_jss_config['domain'] = domain

    quali_jss_api = QualiJSSAPI(quali_jss_config)
    all_suites = quali_jss_api.get_all_suites(jss_domain)
    # quali_jss_api.get_suite_details(domain, 'Quali_test_suite_amf')
    for suite in all_suites:
        suite_id = suite.get('id')
        suite_name = suite.get('name')
        if suite_name == 'AdHoc':
            continue
        if suite_name not in ['AC_AP_AE_ID', 'AC_AP_AE_New', 'ASM_UI_Validation', 'Dashboard TC', 'Dashboard_Closedloop_Executive_view', 'IBM Selenium Debug', 'Impact_Tc','Netcool Selenium Debug', 'Regression_TC', 'Scope_Based_Grouping', 'Smoke_ASM_NoI_Tc', 'Smoke_Installation_TC']:
            continue

        logger.warning(f'Domain {domain} ---Suite {suite_name}/{suite_id} ---  already exists in destination, deleting')
        quali_jss_api.delete_suite(logger, domain, suite_id)


if __name__ == '__main__':
    env = 'lab'

    api = cs_helpers.CloudShellAPISession('cloudshell.vzwnet.com', 'hegdsa8', 'Passwd99%', 'Global')

    domains = cs_helpers.get_all_domains()
    # domains = ['robot']

    for domain in domains:
        logger_config = helpers.read_config('c:/users/hegdsa8/cloudshell_configs/migration_logger_config.json')
        logger = helpers.get_logger(logger_config, f'delete_{domain}')
        print(f'logging to {[h.stream.name for h in logger.handlers]}')
        main(env, domain, logger)
