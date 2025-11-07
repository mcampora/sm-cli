import click
import boto3
from sm.commands.utils import get_domain_id
from sm.commands.projects import get_project
import json

@click.group()
def assets():
    """Manage DataZone assets"""
    pass

@assets.command(name='grant')
@click.option('--domain-id', required=False, help='The ID of the domain (optional if --domain-name is provided)')
@click.option('--domain-name', required=False, help='The name of the domain (optional if --domain-id is provided)')
@click.option('--table', required=True, help='An S3 Table in the form catalog.database.table')
@click.option('--project-name', required=True, help='The project which need access to this location')
@click.option('--account', required=False, default='default', help='The AWS account profile name')
def grant_to_table(domain_id, domain_name, table, project_name, account):
    """
    Grant access to an S3 Table.
    The command assumes you try grant access to a project living in the same account than the table.
    
    Example:
        sm assets grant --domain-name marc_poc --project-name poc_dev --table s3tablescatalog/marc-s3-table-bucket.marc_namespace.sample_table --account dev
    """
    try:
        domain_id = get_domain_id(domain_name, domain_id)

        # look for the project details and id
        project = get_project(domain_id, project_name)
        
        # get the role arn associated to the project from the tooling environment
        environments = project.get('_environments', [])
        project_role_arn = None
        for environment in environments:
            if environment.get('name', '').startswith("Tooling"):
                provisioned_resources = environment.get('_details', {}).get('provisionedResources', [])
                for resource in provisioned_resources:
                    if resource.get('name') == 'userRoleArn':
                        project_role_arn = resource.get('value')
                        break
                if project_role_arn:
                    break
        if not project_role_arn:
            raise click.ClickException(f"Project role not found for project '{project_name}'")
        
        # if the command is called to grant access to a table
        session = boto3.Session(profile_name=account, region_name='us-east-1')
        lakeformation = session.client('lakeformation')
        # Parse table parameter (expected format: catalog.database.table)
        parts = table.split('.')
        if len(parts) == 3:
            catalog_id = parts[0]
            database_name = parts[1]
            table_name = parts[2]    
        else:
            raise click.ClickException(f"Invalid table format. Expected 'catalog.database.table', got '{table}'")
        # Grant Lake Formation permissions on the table
        lakeformation.grant_permissions(
            Principal={
                'DataLakePrincipalIdentifier': project_role_arn
            },
            Resource={
                'Table': {
                    'CatalogId': catalog_id,
                    'DatabaseName': database_name,
                    'Name': table_name
                }
            },
            Permissions=['ALL'],
            PermissionsWithGrantOption=['ALL']
        )
        click.echo(f"✅ Granted ALL permissions (with grant option) on table {database_name}.{table_name} to role {project_role_arn}")
        
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
