import json

import helpers
from lib.QualiJSSAPI import QualiJSSAPI


def main(src_environment, src_domain, dst_environment, dst_domain, logger, old_suite_name, new_suite_name):
    src_config_file = f'c:/cloudshell_configs/{src_environment}.json'
    quali_config = helpers.read_config(src_config_file)
    quali_config['domain'] = src_domain
    quali_jss_config = helpers.read_config(src_config_file)

    quali_jss_api = QualiJSSAPI(quali_jss_config)

    all_suites = quali_jss_api.get_all_suites(src_domain)
    try:
        suite_id = [s.get('id') for s in all_suites if s.get('name') == old_suite_name][0]
    except:
        logger.warning(f'Suite not found: {old_suite_name}')
        return

    suite_details = quali_jss_api.get_suite_details(src_domain, suite_id)

    suite_json = helpers.create_suite_dict_from_jss_suite(logger, suite_details, src_domain, new_suite_name)

    print(suite_json)

    response = quali_jss_api.create_suite(logger, dst_domain, suite_json)
    if not response.ok:
        logger.error(
            f'Failed to create --- Domain {src_domain} ---Suite {suite_name} ---  - {json.loads(response.content)["errors"][0]["message"]}')
    else:
        logger.info(f'Successfully created suite Domain {src_domain} ---Suite {suite_name}')

    # Change owner to SVC-atf-sa-cs
    # response = quali_jss_api.update_suite_owner(logger, dst_domain, suite_name, 'SVC-atf-sa-cs')
    # if not response.ok:
    #     logger.error(f'Failed to update owner to "SVC-atf-sa-cs" Domain {src_domain} ---Suite {suite_name} --- ')
    # else:
    #     logger.info(f'Successfully to update owner to "SVC-atf-sa-cs" Domain {src_domain} ---Suite {suite_name} --- ')


if __name__ == '__main__':
    src_env = 'dev_lab'
    dst_env = 'dev_lab'

    src_domain = 'Automation'
    dst_domain = 'Automation'
    suite_name = 'Sadanand Test 2'
    new_suite_name = f'{suite_name}_new'

    logger_config = helpers.read_config('c:/cloudshell_configs/verification_logger_config.json')
    logger = helpers.get_logger(logger_config, src_domain)
    print(f'logging to {[h.stream.name for h in logger.handlers]}')

    main(src_env, src_domain, dst_env, dst_domain, logger, suite_name, new_suite_name)
