""" This template creates an IAM policy member. """

from hashlib import sha1

mapper = {
    'organizationId': {
        'dm_type': 'gcp-types/cloudresourcemanager-v1:virtual.organizations.iamMemberBinding',
        'dm_resource_property': 'resource',
        'postfix': 'organization'},
    'folderId': {
        'dm_type': 'gcp-types/cloudresourcemanager-v2:virtual.folders.iamMemberBinding',
        'dm_resource_property': 'resource',
        'postfix': 'folder'},
    'projectId': {
        'dm_type': 'gcp-types/cloudresourcemanager-v1:virtual.projects.iamMemberBinding',
        'dm_resource_property': 'resource',
        'postfix': 'project'},
    'bucket': {
        'dm_type': 'gcp-types/storage-v1:virtual.buckets.iamMemberBinding',
        'dm_resource_property': 'bucket',
        'postfix': 'bucket'}
}

resource_map = {
    'folder': {
        'dm_type': 'gcp-types/cloudresourcemanager-v2:virtual.folders.iamMemberBinding',
    },
    'project': {
        'dm_type': 'gcp-types/cloudresourcemanager-v1:virtual.projects.iamMemberBinding'
    },
    'organization': {
        'dm_type': 'gcp-types/cloudresourcemanager-v1:virtual.organizations.iamMemberBinding',
    }
}


def get_node_id(node_type, numeric_id):
    if node_type == 'folder':
        return 'folders/' + str(numeric_id)
    elif node_type == 'project':
        return numeric_id
    elif node_type == 'organization':
        return numeric_id


def generate_config(ctx):
    props = ctx.properties

    node_type = props['node_type']
    node_id = get_node_id(node_type, props['node_id'])
    deployment_name = ctx.env['name']

    node = resource_map[node_type]
    node_dm_type = node['dm_type']

    dm_resources = []

    for role in props['roles']:
        for member in role['members']:
            suffix = sha1('{}-{}'.format(role['role'], member).encode('utf-8')).hexdigest()[:10]
            policy_name = '{}-{}'.format(deployment_name, suffix)
            resource_name = '{}-{}'.format(policy_name, node_type)

            iam_resource = {
                'name': resource_name,
                'type': node_dm_type,
                'properties': {
                    'resource': node_id,
                    'role': role['role'],
                    'member': member,
                }
            }
            dm_resources.append(iam_resource)

    return {'resources': dm_resources}
