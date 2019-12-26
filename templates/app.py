import copy

def generate_config(ctx):
    app_id = ctx.env['name']
    
    props = ctx.properties

    root_node = props['root_node']
    dev_node = props['dev_node']
    prd_node = props['prd_node']
    billing_account_id = props['billing_account_id']

    envs = [
        {'name': 'dev', 'id': dev_node},
        {'name': 'prd', 'id': prd_node}
    ]
    project_configs = make_project_configs(app_id, envs)
    
    resources = []

    # Add projects & associated billing accounts
    resources.extend(
        make_projects_and_billing_accounts(project_configs, billing_account_id)
    )

    # Enable services (APIs) for projects
    for project_config in project_configs:
        project_id = project_config['id']
        services = project_config['services']
        enabled_services_resources = make_enabled_services(project_id, services)
        resources.extend(enabled_services_resources)

    # Delete default network
    for project_config in project_configs:
        # TODO
        if False and project_config['delete_network']:
            delete_network_resources = make_delete_default_network(project_config)
            resources.extend(delete_network_resources)
    
    return {
        'resources': resources,
    }


def make_project_configs(app_id, envs):
    project_configs = []
    services = []
    for env in envs:
        env_name = env['name']
        env_node_id = env['id']
        configs = [
            {
                'id': '{}-{}'.format(app_id, env_name), 
                'parent_id': env_node_id, 
                'services': services,
                'delete_network': True
            },
            {
                'id': '{}-net-{}'.format(app_id, env_name), 
                'parent_id': env_node_id, 
                'services': services,
                'delete_network': True
            },
            {
                'id': '{}-mon-{}'.format(app_id, env_name), 
                'parent_id': env_node_id, 
                'services': services,
                'delete_network': True
            },
        ]
        project_configs.extend(configs)

    return project_configs


def make_projects_and_billing_accounts(project_configs, billing_account_id):
    def make_project(project_config):
        parent_id = project_config['parent_id']
        project_id = project_config['id']
        return {

            'name': project_id,
            'type': 'cloudresourcemanager.v1.project',
            'properties': {
                'name': project_id,
                'projectId': project_id,
                'parent': {
                    'type': 'folder',
                    'id': str(parent_id)
                }
            }
        }

    def make_billing_account(project_id):
        return {
            'name': get_billing_account_name(project_id),
            'type': 'deploymentmanager.v2.virtual.projectBillingInfo',
            'metadata': {
                'dependsOn': [project_id]
            },
            'properties': {
                'name': 'projects/{}'.format(project_id),
                'billingAccountName': 'billingAccounts/{}'.format(billing_account_id)
            }
        }
    
    resources = []
    for project_config in project_configs:
        resources.extend([
            make_project(project_config),
            make_billing_account(project_config['id'])
        ])
    
    return resources


def get_billing_account_name(project_id):
    return '{}-billing'.format(project_id)


def make_billing_accounts(project_ids, billing_account_id):
    def make_billing_account(project_id):
        return {
            'name': get_billing_account_name(project_id),
            'type': 'deploymentmanager.v2.virtual.projectBillingInfo',
            'metadata': {
                'dependsOn': [project_id]
            },
            'properties': {
                'name': 'projects/{}'.format(project_id),
                'billingAccountName': 'billingAccounts/{}'.format(billing_account_id)
            }
        }
    return [make_billing_account(project_id) for project_id in project_ids]


def make_enabled_services(project_id, services):
    dependsOn = [project_id, get_billing_account_name(project_id)]
    resources = []
    for service in services:
        name = '{}-{}'.format(project_id, service)
        consumerId = 'project:{}'.format(project_id)
        resource = {
            'name': name,
            'type': 'deploymentmanager.v2.virtual.enableService',
            'metadata': {
                'dependsOn': dependsOn[:]
            },
            'properties': {
                'consumerId': consumerId,
                'serviceName': service
            }
        }
        dependsOn.append(name)
        resources.append(resource)

    return resources


def make_delete_default_network(project_config):
    default_firewalls = [
        'default-allow-icmp',
        'default-allow-internal',
        'default-allow-rdp',
        'default-allow-ssh',
    ]

    project_id = project_config['id']
    services = project_config['services']

    def make_delete_firewall(firewall_name):
        return {
            'name': '{}-firewall-delete-{}'.format(project_id, firewall_name),
            'action': 'gcp-types/compute-v1:compute.firewalls.delete',
            'metadata': {
                'dependsOn': services
            },
            'properties': {
                'firewall': firewall_name,
                'project': project_id,
            }
        }
    
    delete_firewall_resources = [make_delete_firewall(firewall) for firewall in default_firewalls]    
    network_dependsOn = [resource['name'] for resource in delete_firewall_resources]
    delete_network_resource = {
        'name': '{}-delete-default-network'.format(project_id),
        'action': 'gcp-types/compute-v1:compute.networks.delete',
        'metadata': {
            'dependsOn': network_dependsOn
        },
        'properties': {
                'network': 'default',
                'project': project_id,
        }
    }
    
    resources = []
    resources.append(delete_network_resource)
    resources.extend(delete_firewall_resources)
    return resources
