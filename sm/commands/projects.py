from email.policy import default
import click
import boto3
import json
from sm.commands.utils import get_domain_id
from sm.commands.utils import list_all_projects
from sm.commands.utils import get_profile

@click.command()
@click.option('--domain-id', required=False, help='The ID of the domain (optional if --domain-name is provided)')
@click.option('--domain-name', required=False, help='The name of the domain (optional if --domain-id is provided)')
def list_projects(domain_id, domain_name):
    """List all projects in a DataZone domain.
    
    Example:
        sm list-projects --domain-name my-domain
        sm list-projects --domain-id dzd_xxxxxxxxx
    """
    try:
        domain_id = get_domain_id(domain_name, domain_id)
        projects = list_all_projects(domain_id)
        for project in projects:
            click.echo(f"✅ Found project {project['name']} ({project['id']}) {project['projectStatus']}")
        
    except Exception as e:
        click.echo(f"❌ Error listing projects: {str(e)}", err=True)
        click.get_current_context().exit(1)


@click.command()
@click.option('--domain-id', required=False, help='The ID of the domain (optional if --domain-name is provided)')
@click.option('--domain-name', required=False, help='The name of the domain (optional if --domain-id is provided)')
@click.option('--name', required=True, help='The name of the project')
@click.option('--account', default='default', help='AWS account profile to use')
@click.option('--template', required=True, help='A template used to configure the project.')
def create_project(domain_id, domain_name, name, account, template):
    """Create a new project in the specified domain.
    
    Example:
        sm create-project --domain-name my-domain --name project_name --account dev
        sm create-project --domain-id dzd_xxxxxxxxx --name project_name --account dev
    """
    try:
        session = boto3.Session(profile_name='default')
        datazone = session.client('datazone')

        domain_id = get_domain_id(domain_name, domain_id)
        domain = datazone.get_domain(identifier=domain_id)
        domain_unit_id = domain['rootDomainUnitId']
        project_profile_name = f'Custom_{account}'
        project_profile_id = get_profile(domain_id, project_profile_name)

        with open(template, 'r') as f:
            template = f.read()
        template = template.replace('${DOMAIN_ID}', domain_id)
        template = template.replace('${DOMAIN_UNIT_ID}', domain_unit_id)
        template = template.replace('${PROJECT_NAME}', name)
        template = template.replace('${PROJECT_PROFILE_ID}', project_profile_id)
        if account == 'default':
            branch = 'main'
        else:
            branch = account
        template = template.replace('${BRANCH_NAME}', branch)
        template = template.replace('${ACCOUNT}', account)
        params = json.loads(template)

        owner = params['owner']
        del params['owner']

        project = datazone.create_project(**params)
        del project['ResponseMetadata']
        #click.echo(project)

        # function to search a user profile by email and assign it as owner of a domain unit
        def assign_owner(domain_id, project_id, owner_email):
            click.echo(f"Assigning owner {owner_email} to project {project_id}...")
            users = datazone.search_user_profiles(domainIdentifier=domain_id, userType='SSO_USER', searchText=owner_email)
            if len(users['items']) == 0:
                raise click.BadParameter(f"User {owner_email} not found in domain {domain_id}")
            user = users['items'][0]
            datazone.create_project_membership(
                designation='PROJECT_OWNER',
                domainIdentifier=domain_id,
                member={
                    'userIdentifier': user['id']
                },
                projectIdentifier=project_id
            )
        assign_owner(domain_id, project['id'], owner)

        click.echo(f"✅ Project {name} created successfully!")
               
    except Exception as e:
        click.echo(f"❌ Error creating project: {str(e)}", err=True)
        click.get_current_context().exit(1)

def get_project(domain_id, name):
    session = boto3.Session(profile_name='default')
    datazone = session.client('datazone')
    projects = list_all_projects(domain_id)
    for project in projects:
        if project['name'] == name:
            return project['id']
    raise click.BadParameter(f"Project '{name}' not found in domain '{domain_id}'.")

@click.command()
@click.option('--domain-id', required=False, help='The ID of the domain (optional if --domain-name is provided)')
@click.option('--domain-name', required=False, help='The name of the domain (optional if --domain-id is provided)')
@click.option('--name', required=True, help='The name of the project')
@click.option('--force', is_flag=True, default=False, help='Skip confirmation prompt')
def delete_project(domain_id, domain_name, name, force):
    """Delete a project in the specified domain.
    
    Example:
        sm delete-project --domain-name my-domain --name project_name --force
    """
    try:
        session = boto3.Session(profile_name='default')
        datazone = session.client('datazone')
        domain_id = get_domain_id(domain_name, domain_id)
        project_id = get_project(domain_id, name)

        click.echo(f"\n⚠️  WARNING: You are about to delete the following project:")
        click.echo(f"   Name: {name}")
        click.echo(f"   ID: {project_id}")
        click.echo("\nThis action will permanently delete the project and all its resources!")
        click.echo("This operation cannot be undone!")
            
        if not force:
            if not click.confirm("\nAre you sure you want to delete this project?", default=False):
                click.echo("Deletion canceled!")
                return
            
        click.echo(f"\nDeleting project '{name}' (ID: {project_id})...")

        datazone.delete_project(domainIdentifier=domain_id, identifier=project_id, skipDeletionCheck=True)

        click.echo(f"✅ Project {name} deleted successfully!")
               
    except Exception as e:
        click.echo(f"❌ Error deleting project: {str(e)}", err=True)
        click.get_current_context().exit(1)
