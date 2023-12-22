import re

import cloudshell.helpers.scripts.cloudshell_scripts_helpers as cs_helpers

import helpers


def get_api(quali_config_file='configs/default.json'):
    quali_config = helpers.read_config(quali_config_file)
    cs_api = cs_helpers.CloudShellAPISession(
        quali_config.get('server_name'),
        quali_config.get('username'),
        quali_config.get('password'),
        quali_config.get('domain')
    )
    return cs_api


def get_blueprint_id(blueprint_name, api=None):
    if not api:
        api = get_api()

    # Sample Uri: '/RM/Diagram/Index/eeb190ba-8a4e-4b99-994d-ceb2a7f68ae3?diagramType=Topology&domainId=dbaf480c-09f7-46d3-a2e2-e35d3e374a16'
    blueprint_url = api.GetTopologyUrls(blueprint_name).TopologyUrls[0].EncodedHtmlUri
    blueprint_id = re.search('Index/(.*?)\?', blueprint_url).groups(1)[0]
    return blueprint_id


def get_topologies(api, folder=None, topo_list=None):
    if not topo_list:
        topo_list = list()
    if not api:
        api = get_api()
    if not folder:
        folder = ''
    folders = list()
    contents = api.GetFolderContent(folder)
    if len(contents.ContentArray) == 0:
        return topo_list
    for content in contents.ContentArray:
        if content.Type == 'Folder':
            if folder != '':
                folders.append(folder + '/' + content.Name)
            else:
                folders.append(content.Name)
        elif content.Type == 'Topology':
            topo_list.append(folder + '/' + content.Name)
    for fld in folders:
        get_topologies(api, fld, topo_list)
    return topo_list


def get_all_domains():
    all_groups = api.GetGroupsDetails().Groups
    all_domains = [[d.Name for d in g.TestShellDomains] for g in all_groups if g.Name == 'System Administrators'][0]
    return all_domains


if __name__ == '__main__':
    api = get_api('configs/vzw.json')
    # bp_id = get_blueprint_id('CDS OPS topologies/Visible WSG-Consecutive', api)
    # print(bp_id)
    topology_list = get_topologies(api, '')
    print(topology_list)
