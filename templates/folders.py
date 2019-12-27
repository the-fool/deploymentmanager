import copy

def generate_config(ctx):
    props = ctx.properties
    app_id = ctx.env['name']
    parent_node = props['parent_node']
    root_parent_type = parent_node.get('type')
    root_parent_id = parent_node.get('id')
    root_parent = '{}s/{}'.format(root_parent_type, root_parent_id)

    folder_resource = {
        'name': app_id,
        'type': 'gcp-types/cloudresourcemanager-v2:folders',
        'properties': {
            'parent': root_parent,
            'displayName': app_id
        }
    }
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

    resources = [
        folder_resource,
        folder_dev_resource,
        folder_prod_resource,
    ]

    return {
        'resources': resources,
        'outputs': [
            {'name': 'dev', 'value': '$(ref.{}.name)'.format(dev_folder)},
            {'name': 'prd', 'value': '$(ref.{}.name)'.format(prd_folder)},
        ]
    }