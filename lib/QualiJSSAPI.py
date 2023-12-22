import json
import requests


class QualiJSSAPI:
    def __init__(self, config):
        """
        :param config:
        """
        self.server_addr = config.get('jss_server_name')
        self.port = config.get('jss_port')
        self.username = config.get('username')
        self.password = config.get('password')
        self.domain = config.get('domain')
        self.url = f'http://{self.server_addr}'
        self.headers = {'accept': 'text/plain', 'Content-Type': 'application/json'}
        self.auth_code = ''
        self.get_token()
        # self.login()

    def get_token(self):
        response = requests.post(
            url=f'{self.url}/api/Account/login',
            json={'username': self.username, 'password': self.password},
            headers=self.headers,
            verify=False
        )
        self.auth_code = f'Bearer {response.json().get("accessToken")}'
        self.headers.update({'Authorization': self.auth_code})

    def get_all_suites(self, domain_name):
        endpoint = f'/api/spaces/{domain_name}/SuiteTemplate/Summary'
        url = f'{self.url}{endpoint}'
        r = requests.get(
            url=url,
            headers=self.headers,
            verify=False
        )
        suites = json.loads(r.content.decode('utf-8'))
        return suites

    def get_dashboard(self, domain_name):
        endpoint = f'/api/spaces/{domain_name}/SuiteTemplate/dashboard'
        url = f'{self.url}{endpoint}'
        r = requests.get(
            url=url,
            headers=self.headers,
            verify=False
        )
        suites = json.loads(r.content.decode('utf-8'))
        return suites

    def get_suite_details(self, domain_name, suite_id):
        endpoint = f'/api/spaces/{domain_name}/SuiteTemplate/{suite_id}'
        url = f'{self.url}{endpoint}'

        r = requests.get(
            url=url,
            headers=self.headers,
            verify=False
        )
        suite_details = json.loads(r.content)
        return suite_details

    def create_suite(self, logger, domain_name, suite_details):
        endpoint = f'/api/spaces/{domain_name}/SuiteTemplate/'
        url = f'{self.url}{endpoint}'

        response = requests.post(url, json=suite_details, headers=self.headers, verify=False)
        if not response.ok:
            logger.error(f'Failed to create suite: {suite_details}, error:{response.text}')
        return response

    def delete_suite(self, logger, domain_name, suite_id):
        endpoint = f'/api/spaces/{domain_name}/SuiteTemplate/{suite_id}'
        url = f'{self.url}{endpoint}'

        response = requests.delete(url, headers=self.headers, verify=False)
        if not response.ok:
            logger.error(f'Failed to create suite: {suite_details}, error:{response.text}')
        return response

    def update_suite_owner(self, logger, domain_name, suite_name, owner_name):
        suites = self.get_all_suites(domain_name)
        suite_id = [suite.get('id') for suite in suites if suite.get('name') == suite_name][0]

        endpoint = f'/api/spaces/{domain_name}/SuiteTemplate/{suite_id}/changeowner'
        url = f'{self.url}{endpoint}'
        json_payload = {"ownerUsername": owner_name}

        response = requests.put(url, json=json_payload, headers=self.headers, verify=False)
        if not response.ok:
            logger.error(f'Failed to create suite: {suite_details}, error:{response.text}')
        return response

    def stop_suite_execution(self, logger, domain_name, suite_name):
        endpoint = f'/api/spaces/{domain_name}/SuiteTemplate/{suite_id}/changeowner'

    def get_tests(self, domain_name):
        endpoint = f'/api/spaces/{domain_name}/Test'
        url = f'{self.url}{endpoint}'

        r = requests.get(
            url=url,
            headers=self.headers,
            verify=False
        )
        tests = json.loads(r.content)
        return tests

    def download_report(self, test_id):
        endpoint = f'/api/spaces/robot/TestExecution/{test_id}/Report/download'
        url = f'{self.url}{endpoint}'

        r = requests.get(
            url=url,
            headers=self.headers,
            verify=False
        )

        print(r.content)
        return r.content


if __name__ == '__main__':
    import helpers

    domain = 'PIP'
    logger_config = helpers.read_config(r'c:/users/hegdsa8/cloudshell_configs/logger_config.json')
    logger = helpers.get_logger(logger_config, prefix='')

    quali_jss_config = helpers.read_config(r'c:/users/hegdsa8/cloudshell_configs/lab.json')
    quali_jss_config['domain'] = domain
    quali_jss_api = QualiJSSAPI(quali_jss_config)
    tests = quali_jss_api.get_tests(domain)
    suites = quali_jss_api.get_all_suites(quali_jss_config.get('domain'))
    # pprint(suites)
    #
    # # id = suites[0].get('id')
    # for suite in suites:
    #     if suite.get('name') == 'Combined Visible Health check--DEBUG':
    #         id = suite.get('id')
    #         suite_details = quali_jss_api.get_suite_details(quali_jss_config.get('domain'), id)
    # pprint(suite_details)

    suite_id = [suite.get('id') for suite in suites if suite.get('name') == 'Simulation 5gNode - 0'][0]
    suite_details = quali_jss_api.get_suite_details(domain, suite_id)
    suite_owner = suite_details.get('ownerUsername')
    print(f'Current owner: {suite_owner}')
    quali_jss_api.update_suite_owner(logger, 'CDS OPS', 'Combined Visible Health check--DEBUG', 'hegdsa8')
