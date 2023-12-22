import helpers
from lib.QualiJSSAPI import QualiJSSAPI


def download_report(jss_config, execution_id):
    quali_jss_api = QualiJSSAPI(jss_config)
    report = quali_jss_api.download_report(execution_id)
    print(report)


if __name__ == '__main__':
    domains = ['robot']
    environment = 'local'
    tst_execution_id = 'e6341e81-e530-41ce-93ee-9738d363c22c'

    dst_config_file = f'c:/CloudShellConfigs/{environment}.json'
    quali_jss_config = helpers.read_config(dst_config_file)
    for cs_domain in domains:
        print(download_report(quali_jss_config, tst_execution_id))
