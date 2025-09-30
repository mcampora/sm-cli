import click
import boto3
from sm.commands.utils import get_domain_id

@click.group()
def assets():
    """Manage DataZone assets"""
    pass

@assets.command(name='grant-access')
@click.option('--domain-id', required=False, help='The ID of the domain (optional if --domain-name is provided)')
@click.option('--domain-name', required=False, help='The name of the domain (optional if --domain-id is provided)')
@click.option('--location', required=True, help='The S3 location')
@click.option('--project-name', required=True, help='The project which need access to this location')
@click.option('--account', required=False, default='default', help='The AWS account profile name')
def grant_access(domain_id, domain_name, location, project_name, account):
    """Grant access to an S3 location."""
    try:
        domain_id = get_domain_id(domain_name, domain_id)
        session = boto3.Session(profile_name=account)
        lakeformation = session.client('lakeformation')

        # get the project details
        # get the role arn associated to the project
        # grant permissions to the role arn on the location

        click.echo(f"Granting access to {location} on project {project_name} in domain {domain_id}.")

    except Exception as e:
        click.echo(f"❌ Error granting access: {str(e)}", err=True)
        click.get_current_context().exit(1)

def register_commands(cli):
    """Register asset commands with the main CLI"""
    cli.add_command(assets)
