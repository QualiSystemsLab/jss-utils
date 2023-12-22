from lib.QualiJSSAPI import QualiJSSAPI

import helpers


def get_suites(jss_config, domain):
    jss_config['domain'] = domain

    quali_jss_api = QualiJSSAPI(jss_config)
    suites = quali_jss_api.get_all_suites(domain)
    if isinstance(suites, list):
        suite_names = [(s['name'], s['id']) for s in suites]
        return suite_names


if __name__ == '__main__':
    domains = ['robot']
    environment = 'local'

    dst_config_file = f'c:/CloudShellConfigs/{environment}.json'
    quali_jss_config = helpers.read_config(dst_config_file)
    for cs_domain in domains:
        print(get_suites(quali_jss_config, cs_domain))
