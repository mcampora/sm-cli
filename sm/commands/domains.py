import click
import boto3
from pprint import pformat
import json
from sm.commands.utils import get_domain_id, delete_resource_shares, list_all_projects

# ----------------------------------------
# TODO
# create the domain roles if missing
# ----------------------------------------

@click.command()
def list_domains():
    """List SageMaker domains in the current AWS account with details."""
    try:
        datazone = boto3.client('datazone')
        domains = datazone.list_domains()['items']
        
        if not domains:
            click.echo("No SageMaker domains found.")
            return

        for domain_summary in domains:
            domain_id = domain_summary['id']
            try:
                details = datazone.get_domain(identifier=domain_id)
                click.echo(f"- {details['name']} {domain_id} {details['status']} {details['portalUrl']}")

            except Exception as detail_error:
                click.echo(f"\n- Could not get details for Domain ID: {domain_id}")
                click.echo(f"  Error: {str(detail_error)}", err=True)

    except Exception as e:
        click.echo(f"❌ Error listing SageMaker domains: {str(e)}", err=True)
        click.get_current_context().exit(1)

@click.command()
@click.option('--id', 'domain_id', required=False, help='The ID of the domain to describe')
@click.option('--name', 'domain_name', required=False, help='The Name of the domain to describe')
def describe_domain(domain_id, domain_name):
    """
    Display detailed information about a specific domain.
    Return a JSON document.

    Example:
        sm describe-domain --id dzd_4s9s40qvcqalpj
    """
    try:
        datazone = boto3.client('datazone')
        result = {}
        domain_id = get_domain_id(domain_name, domain_id)

        # Get domain details
        domain = datazone.get_domain(identifier=domain_id)
        del domain['ResponseMetadata']
        result['_domain'] = domain

        # Get the list of domain units, build a hierarchical structure, and include the users details
        def get_domain_units(domain_id, parent_unit_id, parent_unit_name):
            res = { '_id': parent_unit_id, '_name': parent_unit_name }
            domain_unit_users = datazone.list_entity_owners(domainIdentifier=domain_id, entityIdentifier=parent_unit_id, entityType='DOMAIN_UNIT')['owners']
            for user in domain_unit_users:
                user_id = user['user']['userId']
                user_details = datazone.get_user_profile(domainIdentifier=domain_id, userIdentifier=user_id, type='SSO')['details']
                user['user']['_user_details'] = user_details
            res['_users'] = domain_unit_users
            child_domain_units = datazone.list_domain_units_for_parent(domainIdentifier=domain_id, parentDomainUnitIdentifier=parent_unit_id)['items']
            res['_children'] = []
            for child_domain_unit in child_domain_units:
                res['_children'].append(get_domain_units(domain_id, child_domain_unit['id'], child_domain_unit['name']))
            return res
        root_unit_id = domain['rootDomainUnitId']
        root_unit_name = domain['name']
        domain_units = get_domain_units(domain_id, root_unit_id, root_unit_name)
        result['_domain_units'] = domain_units

        for flag in [ True, False ]:
            response = datazone.list_environment_blueprints(
                domainIdentifier=domain_id,
                managed=flag,
                maxResults=50
            )
            result['_environment_blueprints_' + str(flag)] = response['items']
            for environment_blueprint in response['items']:
                environment_blueprint['_details'] = datazone.get_environment_blueprint(domainIdentifier=domain_id, identifier=environment_blueprint['id'])
                del environment_blueprint['_details']['ResponseMetadata']
        

        response = datazone.list_environment_blueprint_configurations(
            domainIdentifier=domain_id
        )
        result['_environment_blueprint_configurations'] = response['items']
        for environment_blueprint_configuration in response['items']:
            environment_blueprint_configuration['_details'] = datazone.get_environment_blueprint_configuration(domainIdentifier=domain_id, environmentBlueprintIdentifier=environment_blueprint_configuration['environmentBlueprintId'])
            del environment_blueprint_configuration['_details']['ResponseMetadata']

        response = datazone.list_project_profiles(
            domainIdentifier=domain_id,
        )
        result['_project_profiles'] = response['items']
        for project_profile in response['items']:
            project_profile['_details'] = datazone.get_project_profile(domainIdentifier=domain_id, identifier=project_profile['id'])
            del project_profile['_details']['ResponseMetadata']

        result['_projects'] = list_all_projects(domain_id)

        # v1 API
        # response = datazone.list_environment_profiles(
        #    domainIdentifier=domain_id
        # )

        # unused functions
        # get_data_source
        # get_domain_unit
        # get_environment_profile

        # Get the list of associated accounts
        pools = datazone.list_account_pools(domainIdentifier=domain_id)['items']
        for pool in pools:
            accounts = datazone.list_accounts_in_account_pool(domainIdentifier=domain_id, identifier=pool['id'])['items']
            pool['_accounts'] = accounts
        result['_pools'] = pools
            
        click.echo(json.dumps(result, default=str, indent=4))    

    except Exception as e:
        click.echo(f"❌ Error describing domain {domain_id}: {str(e)}", err=True)
        click.get_current_context().exit(1)

@click.command()
@click.option('--manifest', required=True, help='Name of the file describing the domain to create')
def create_domain(manifest):
    """Create a new DataZone domain with the specified parameters.
    
    Example:
        sm create-domain --manifest marc_test.json
    """
    try:
        datazone = boto3.client('datazone')
        
        # load the manifest
        params = json.load(open(manifest))
        
        # prepare the create domain parameters
        create_domain_params = {
            'name': params['name'],
            'domainExecutionRole': params['domainExecutionRole'],
            'serviceRole': params['serviceRole'],
            'domainVersion': 'V2',
            'singleSignOn': {
                'idcInstanceArn': params['identitycenter'],
                'type': 'IAM_IDC',
                'userAssignment': 'AUTOMATIC'
            }
        }
        if 'tags' in params:
            create_domain_params['tags'] = params['tags']
        
        # create the domain
        click.echo(f"Creating domain '{params['name']}'...")
        response = datazone.create_domain(**create_domain_params)
        domain_id = response['id']
        
        # function to search a user profile by email and assign it as owner of a domain unit
        def assign_owner(domain_id, entity_id, owner_email):
            user = datazone.search_user_profiles(domainIdentifier=domain_id, userType='SSO_USER', searchText=owner_email)['items'][0]
            datazone.add_entity_owner(
                domainIdentifier=domain_id, 
                entityIdentifier=entity_id, 
                entityType='DOMAIN_UNIT', 
                owner={ 'user': { 'userIdentifier': user['id'] } } )
        
        # recursive function used to create the domain units
        def create_domain_unit(domain_id, parent_domain_unit_id, domain_units):
            for domain_unit in domain_units:
                response = datazone.create_domain_unit(domainIdentifier=domain_id, parentDomainUnitIdentifier=parent_domain_unit_id, name=domain_unit['name'])
                assign_owner(domain_id, response['id'], domain_unit['owner'])
                if 'children' in domain_unit:
                    create_domain_unit(domain_id, response['id'], domain_unit['children'])
        
        # get the root domain unit and assign its owner
        domain = datazone.get_domain(identifier=domain_id)
        root_domain_unit_id = domain['rootDomainUnitId']
        assign_owner(domain_id, root_domain_unit_id, params['owner'])
        
        # create the domain units
        create_domain_unit(domain_id, root_domain_unit_id, params['domainUnits'])
                          
        # Display the domain details
        click.echo(f"✅ Domain creation initiated for '{params['name']}' (ID: {domain_id}).")
        click.echo(f"\nDomain Information:")
        click.echo(f"  Name: {params['name']}")
        click.echo(f"  ID: {domain_id}")
        click.echo(f"  Status: {response.get('status', 'CREATING')}")
        if 'portalUrl' in response:
            click.echo(f"  Portal URL: {response['portalUrl']}")
        
        return response
        
    except Exception as e:
        click.echo(f"❌ Error creating domain: {str(e)}", err=True)
        click.get_current_context().exit(1)

@click.command()
@click.option('--id', 'domain_id', required=False, help='ID of the domain to delete')
@click.option('--name', 'domain_name', required=False, help='The Name of the domain to delete')
@click.option('--force', is_flag=True, help='Skip confirmation prompt')
def delete_domain(domain_id, domain_name, force):
    """Delete a DataZone domain and its associated resources.
    
    This will permanently delete the domain and all its associated resources.
    Use with caution as this action cannot be undone.
    
    Example:
        sm delete-domain --id dzd_xxxxxxxxx
    """
    try:
        domain_id = get_domain_id(domain_name, domain_id)

        datazone = boto3.client('datazone')
        
        # Get domain details to show user what will be deleted
        domain = datazone.get_domain(identifier=domain_id)
        domain_name = domain.get('name', 'Unknown')
        click.echo(f"\n⚠️  WARNING: You are about to delete the following domain:")
        click.echo(f"   Name: {domain_name}")
        click.echo(f"   ID: {domain_id}")
        click.echo(f"   Status: {domain.get('status', 'UNKNOWN')}")
        if 'portalUrl' in domain:
            click.echo(f"   Portal URL: {domain['portalUrl']}")
        click.echo("\nThis action will permanently delete the domain and all its resources!")
        click.echo("This operation cannot be undone!")
            
        if not force:
            if not click.confirm("\nAre you sure you want to delete this domain?", default=False):
                click.echo("Deletion canceled!")
                return
            
        click.echo(f"\nDeleting domain '{domain_name}' (ID: {domain_id})...")
            
        # Delete the resource shares
        delete_resource_shares(domain_id)

        # Delete the domain
        response = datazone.delete_domain(identifier=domain_id)
            
        click.echo(f"✅ Domain '{domain_name}' has been successfully deleted.")
            
        return response
            
    except Exception as e:
        click.echo(f"❌ Error deleting domain: {str(e)}", err=True)
        click.get_current_context().exit(1)
