import click
import boto3
from sm.commands.utils import get_domain_id
from sm.commands.projects import get_project
import json

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

@assets.command(name='publish')
@click.option('--domain-id', required=False, help='The ID of the domain (optional if --domain-name is provided)')
@click.option('--domain-name', required=False, help='The name of the domain (optional if --domain-id is provided)')
@click.option('--project-name', required=True, help='The name of the project where the asset will be published')
@click.option('--asset-name', required=True, help='The name of the asset to be published')
@click.option('--account', required=False, default='default', help='The AWS account profile name')
def publish(domain_id, domain_name, project_name, asset_name, account):
    """Publish a data asset in DataZone."""
    try:
        domain_id = get_domain_id(domain_name, domain_id)
        project = get_project(domain_id, project_name)
        project_id = project['id']

        session = boto3.Session(profile_name=account, region_name='us-east-1')
        datazone = session.client('datazone')

        table = {
            'databaseName':'prod_poc_prod_glue_db',
            'tableName':'silver',
            'catalogId':'183631307357',
            'region':'us-east-1',
            'tableArn':'arn:aws:glue:us-east-1:183631307357:table/prod_poc_prod_glue_db/silver',
            'columns':[
                {
                    'columnName':'nb_products',
                    'dataType':'int'
                },
                {
                    'columnName':'nb_items',
                    'dataType':'int'
                }
            ]
        }

        asset = {
            'domainIdentifier': domain_id,
            'owningProjectIdentifier': project_id,
            'name': asset_name,
            'typeIdentifier': 'amazon.datazone.GlueTableAssetType',
            'formsInput': [
                {
                    'formName': 'GlueTableForm',
                    'typeIdentifier': 'amazon.datazone.GlueTableFormType',
                    'typeRevision': '13',
                    'content': json.dumps(table)
                }
            ]
        }
      
        click.echo(json.dumps(asset, indent=2, default=str))

        result = datazone.create_asset(**asset)

        click.echo(f"Publishing asset '{asset_name}' in project '{project_name}' in domain '{domain_id}'.")

        del result['ResponseMetadata']
        click.echo(result)

    except Exception as e:
        click.echo(f"❌ Error publishing asset: {str(e)}", err=True)
        click.get_current_context().exit(1)

def register_commands(cli):
    """Register asset commands with the main CLI"""
    cli.add_command(assets)
