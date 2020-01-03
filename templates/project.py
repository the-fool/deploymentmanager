import copy


def generate_config(ctx):
    props = ctx.properties
    project_id = ctx.env['name']
    project_name = project_id
    billing_account_deployment_name = project_name + '-billing'
    billing_account_id = props['billing_account_id']
    parent_node = props['parent_node']
    parent_node['id'] = str(parent_node['id'])
    apis = props.get('apis', [])

    # Create Project
    project_resource = {
        'name': project_id,
        'type': 'cloudresourcemanager.v1.project',
        'properties': {
                'name': project_name,
                'projectId': project_id,
                'parent': parent_node
        }
    }

    # Create Billing Account
    billing_account_resource = {
            'name': billing_account_deployment_name,
            'type': 'deploymentmanager.v2.virtual.projectBillingInfo',
            'metadata': {
                'dependsOn': [project_id]
            },
            'properties': {
                'name': 'projects/' + project_id,
                'billingAccountName': 'billingAccounts/' + billing_account_id
            }
    }

    # Create API Resources
    api_resources = []
    api_deps = [project_id, billing_account_deployment_name]
    for i, api in enumerate(apis):
        name = project_id + '-' + api
        api_resource = {
            'name': name,
            'type': 'deploymentmanager.v2.virtual.enableService',
            'metadata': {
                'dependsOn': api_deps[:]
            },
            'properties': {
                'consumerId': 'project:'+project_id,
                'serviceName': api
            }
        }
        api_resources.append(api_resource)
        api_deps.append(name)

    resources = [
        project_resource,
        billing_account_resource,
    ]
    resources.extend(api_resources)

    return {
        'resources': resources
    }
