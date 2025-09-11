import click
import boto3
import json
import os
from sm.commands.utils import get_domain_id
from sm.commands.utils import list_all_projects

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
        click.echo(json.dumps(projects, indent=2, default=str))
        
    except Exception as e:
        click.echo(f"❌ Error listing projects: {str(e)}", err=True)
        click.get_current_context().exit(1)


def get_project_profile(environment):
    """Return the project profile ARN based on environment."""
    profiles = {
        'dev': 'arn:aws:datazone:us-east-1:123456789012:project-profile/dev-profile',
        'test': 'arn:aws:datazone:us-east-1:123456789012:project-profile/test-profile',
        'prod': 'arn:aws:datazone:us-east-1:123456789012:project-profile/prod-profile'
    }
    return profiles.get(environment.lower(), profiles['dev'])


@click.command()
@click.option('--domain-id', required=False, help='The ID of the domain (optional if --domain-name is provided)')
@click.option('--domain-name', required=False, help='The name of the domain (optional if --domain-id is provided)')
@click.option('--name', required=True, help='Name of the project to create')
@click.option('--description', default='', help='Description of the project')
@click.option('--environment', type=click.Choice(['dev', 'test', 'prod'], case_sensitive=False), 
              default='dev', help='Environment for the project (dev/test/prod)')
@click.option('--profile', default='default', help='AWS profile to use')
def create_project(domain_id, domain_name, name, description, environment, profile):
    """Create a new project in the specified domain.
    
    Example:
        sm create-project --domain-name my-domain --name my-project --environment dev
        sm create-project --domain-id dzd_xxxxxxxxx --name my-project --environment test
    """
    try:
        # Set the AWS profile
        boto3.setup_default_session(profile_name=profile)
        
        # Get the domain ID
        domain_id = get_domain_id(domain_name, domain_id)
        
        # Get the appropriate project profile based on environment
        project_profile_arn = get_project_profile(environment)
        
        # Initialize the DataZone client with the specified profile
        datazone = boto3.client('datazone')
        
        # Create the project
        response = datazone.create_project(
            domainIdentifier=domain_id,
            name=name,
            description=description,
            projectProfile=project_profile_arn
        )
        
        # Get the project details
        project_id = response['id']
        project_details = datazone.get_project(
            domainIdentifier=domain_id,
            identifier=project_id
        )
        
        click.echo("✅ Project created successfully!")
        click.echo(json.dumps(project_details, indent=2, default=str))
        
        return project_details
        
    except Exception as e:
        click.echo(f"❌ Error creating project: {str(e)}", err=True)
        click.get_current_context().exit(1)
