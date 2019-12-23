import copy

def generate_config(ctx):
    props = ctx.properties
    app_id = ctx.env['name']
    parent_node = props['parent_node']

    # Create Root Folder
    root_parent_type = parent_node.get('type')
    root_parent_id = parent_node.get('id')
    root_parent = f'{root_parent_type}s/{root_parent_id}'
    folder_resource = {
        'name': app_id,
        'type': 'gcp-types/cloudresourcemanager-v2:folders',
        'properties': {
            'parent': root_parent,
            'displayName': app_id
        }
    }
    root_id = f'$(ref.{app_id}.name)'

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

    prd_folder_id = f'$(ref.{prd_folder}.name)'
    dev_folder_id = f'$(ref.{dev_folder}.name)'
    # Create dev project
    dev_project_id = f'{app_id}-project-dev'

    dev_project_resource = {
        'name': dev_project_id,
        'type': 'cloudresourcemanager.v1.project',
        'metadata': {
            'dependsOn': [
                dev_folder,
                prd_folder
            ]
        },
        'properties': {
            'name': dev_project_id,
            'projectId': dev_project_id,
            'parent': {
                'type': 'folder',
                'id': dev_folder_id.replace('folders/', '')
            }
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
            {'name': 'dev', 'value': f'$(ref.{dev_folder}.name)'},
            {'name': 'prd', 'value': f'$(ref.{prd_folder}.name)'},
        ]
    }