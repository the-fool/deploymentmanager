def generate_config(ctx):
    props = ctx.properties
    name = ctx.env['name']
    vpc_self_link = '$(ref.{}.selfLink)'.format(name)

    vpc_resource = {
        'type': 'gcp-types/compute-v1:networks',
        'name': name,
        'properties': {
            'project': props['project_id'],
            'name': name,
            'autoCreateSubnetworks': False
        }
    }

    subnets = props.get('subnets', [])
    subnet_resources = []
    for i, subnet in enumerate(subnets):
        subnet_resource = {
            'type': 'gcp-types/compute-v1:subnetworks',
            'name': subnet['name'],
            'properties': {
                'project': props['project_id'],
                'network': vpc_self_link,
                'ipCidrRange': subnet['ipCidrRange'],
                'region': subnet['region']
            }
        }
        subnet_resources.append(subnet_resource)

    resources = [
        vpc_resource,
    ]
    resources.extend(subnet_resources)

    return {
        'resources': resources
    }
