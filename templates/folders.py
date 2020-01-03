def generate_config(ctx):
    props = ctx.properties
    app_id = ctx.env['name']
    parent_node = props['parent_node']
    owners = props['owners']
    root_parent_type = parent_node.get('type')
    root_parent_id = parent_node.get('id')
    root_parent = '{}s/{}'.format(root_parent_type, root_parent_id)

    resources = []

    folder_resource = {
        'name': app_id,
        'type': 'gcp-types/cloudresourcemanager-v2:folders',
        'properties': {
            'parent': root_parent,
            'displayName': app_id
        }
    }

    resources.append(folder_resource)

    root_id = '$(ref.{}.name)'.format(app_id)

    # Create Env Folders
    dev_folder = app_id + '-DEV'
    folder_dev_resource = {
        'name': dev_folder,
        'type': 'gcp-types/cloudresourcemanager-v2:folders',
        'metadata': {
            'dependsOn': [app_id]
        },
        'properties': {
            'parent': root_id,
            'displayName': dev_folder
        }
    }
    resources.append(folder_dev_resource)

    prd_folder = app_id + '-PRD'
    folder_prod_resource = {
        'name': prd_folder,
        'metadata': {
            'dependsOn': [app_id]
        },
        'type': 'gcp-types/cloudresourcemanager-v2:folders',
        'properties': {
            'parent': root_id,
            'displayName': prd_folder
        }
    }
    resources.append(folder_prod_resource)

    roles = [
        'roles/editor', 
        'roles/resourcemanager.projectCreator',
        'roles/iam.securityAdmin',
        'roles/resourcemanager.folderAdmin'
    ]
    for role in roles:
        for owner in owners:
            iam_binding = {
                'name': '{}-{}'.format(owner, role),
                'type': 'gcp-types/cloudresourcemanager-v2:virtual.folders.iamMemberBinding',
                'metadata': {
                    'dependsOn': [app_id]
                },
                'properties': {
                    'resource': '$(ref.{}.name)'.format(app_id),
                    'role': role,
                    'member': owner
                }
            }
            resources.append(iam_binding)

    return {
        'resources': resources,
        'outputs': [
            {'name': 'dev', 'value': '$(ref.{}.name)'.format(dev_folder)},
            {'name': 'prd', 'value': '$(ref.{}.name)'.format(prd_folder)},
        ]
    }
