import click
import json
import boto3
from sm.commands.utils import get_domain_id
from sm.commands.projects import get_project
import time
import sys

@click.group()
def workflows():
    """Manage workflow environments"""
    pass


def get_environment(domain_id, name):
    project = get_project(domain_id, name)
    if not project:
        raise click.BadParameter(f"Project '{name}' not found in domain '{domain_id}'.")
    environments = project.get('_environments', [])
    environment = None
    for item in environments:
        if item.get('name', '').startswith("workflow"):
            environment = item
            break
    return environment


def get_environment_name(domain_id, project_name):
    environment = get_environment(domain_id, project_name)                
    if not environment:
        raise click.BadParameter(f"Workflow environment not found in project '{project_name}'.")
    rscs = environment.get('_details', {}).get('provisionedResources', {})
    name = None
    for rsc in rscs:
        if rsc.get('name') == "mwaaEnvironmentArn":
            name = rsc.get('value').split('/')[-1]
            break
    return name


@workflows.command(name='describe')
@click.option('--domain-id', required=False, help='The ID of the domain (optional if --domain-name is provided)')
@click.option('--domain-name', required=False, help='The name of the domain (optional if --domain-id is provided)')
@click.option('--name', required=True, help='The name of the project to retrieve')
@click.option('--short', is_flag=True, default=False, help='Display only basic environment details')
def describe(domain_id, domain_name, name, short):
    """Get workflow environment details for a project.
    
    The output includes workflow-specific environment details in JSON format.
    
    Example:
        sm workflows describe-env --domain-name my-domain --name project_name
        sm workflows describe-env --domain-id dzd_xxxxxxxxx --name project_name
    """
    try:
        domain_id = get_domain_id(domain_name, domain_id)
        environment = get_environment(domain_id, name)                
        if not environment:
            raise click.BadParameter(f"Workflow environment not found in project '{name}'.")
            
        if short:
            rscs = environment.get('_details', {}).get('provisionedResources', {})
            click.echo(json.dumps(rscs, indent=2, default=str))
        else:
            click.echo(json.dumps(environment.get('_details', {}), indent=2, default=str))

    except Exception as e:
        click.echo(f"❌ Error getting workflow environment details: {str(e)}", err=True)
        click.get_current_context().exit(1)


@workflows.command(name='list-dags')
@click.option('--domain-id', required=False, help='The ID of the domain (optional if --domain-name is provided)')
@click.option('--domain-name', required=False, help='The name of the domain (optional if --domain-id is provided)')
@click.option('--project-name', required=True, help='The name of the project to retrieve')
@click.option('--account', required=True, default='default', help='The AWS account profile name')
def list_dags(domain_id, domain_name, project_name, account):
    """List DAGs in a project's workflow environment."""
    try:
        domain_id = get_domain_id(domain_name, domain_id)
        name = get_environment_name(domain_id, project_name)
        if not name:
            raise click.BadParameter(f"MWAA environment ARN not found in project '{project_name}'.")
        #click.echo(name)
        session = boto3.Session(profile_name=account, region_name='us-east-1')
        client = session.client("mwaa")
        request_params = {
            "Name": name,
            "Path": "/dags",
            "Method": "GET",
            "QueryParameters": { "paused": False }
        }
        response = client.invoke_rest_api(**request_params)
        for dag in response['RestApiResponse']['dags']:
            dag_id = dag['dag_id']
            dag_name = dag['dag_display_name']
            click.echo(f"{dag_name} - {dag_id}")
        #click.echo(json.dumps(response['RestApiResponse'], indent=2, default=str))
    except Exception as e:
        click.echo(f"❌ Error listing dags: {str(e)}", err=True)
        click.get_current_context().exit(1)


def trigger_dag(client, env_name, dag_name):
    request_params = {
        "Name": env_name,
        "Path": f"/dags/{dag_name}/dagRuns",
        "Method": "POST"
    }
    response = client.invoke_rest_api(**request_params)
    run_id = response['RestApiResponse']['dag_run_id']
    return run_id


def wait_for_dag(client, env_name, dag_name, run_id):
    request_params = {
        "Name": env_name,
        "Path": f"/dags/{dag_name}/dagRuns/{run_id}",
        "Method": "GET"
    }
    t = 30
    status = 'failed'
    while True:
        response = client.invoke_rest_api(**request_params)
        status = response['RestApiResponse']['state']
        if status != 'running' and status != 'queued':
            break
        else:
            click.echo(f"✅ DAGrun '{run_id}' status: {status} (waiting {t} seconds...)")
        time.sleep(t)
    return status


@workflows.command(name='run-dag')
@click.option('--domain-id', required=False, help='The ID of the domain (optional if --domain-name is provided)')
@click.option('--domain-name', required=False, help='The name of the domain (optional if --domain-id is provided)')
@click.option('--project-name', required=True, help='The name of the project to retrieve')
@click.option('--name', required=True, help='The name of the DAG to execute')
@click.option('--account', required=True, default='default', help='The AWS account profile name')
@click.option('--wait', is_flag=True, default=False, help='Wait for completion')
def run_dag(domain_id, domain_name, project_name, name, account, wait):
    """Trigger the execution of a specific DAG in a project's workflow environment."""
    try:
        domain_id = get_domain_id(domain_name, domain_id)
        env_name = get_environment_name(domain_id, project_name)                
        if not name:
            raise click.BadParameter(f"MWAA environment ARN not found in project '{name}'.")
        session = boto3.Session(profile_name=account, region_name='us-east-1')
        client = session.client("mwaa")
        run_id = trigger_dag(client, env_name, name)
        if wait == True:
            status = wait_for_dag(client, env_name, name, run_id)
            click.echo(f"✅ DAG '{name}' / '{run_id}' / status: {status}")
            if status != 'success':
                raise click.ClickException(f"DAG '{name}' failed with status: {status}")
        else:
            click.echo(f"✅ DAG '{name}' triggered with run ID: {run_id}")
    except Exception as e:
        click.echo(f"❌ Error running dag: {str(e)}", err=True)
        click.get_current_context().exit(1)


@workflows.command(name='check-dag')
@click.option('--domain-id', required=False, help='The ID of the domain (optional if --domain-name is provided)')
@click.option('--domain-name', required=False, help='The name of the domain (optional if --domain-id is provided)')
@click.option('--project-name', required=True, help='The name of the project to retrieve')
@click.option('--name', required=True, help='The name of the DAG to execute')
@click.option('--run-id', required=True, help='The run ID of the DAG to check')
@click.option('--account', required=True, default='default', help='The AWS account profile name')
def check_dag(domain_id, domain_name, project_name, name, run_id, account):
    """Check the status of a specific DAG in a project's workflow environment."""
    try:
        domain_id = get_domain_id(domain_name, domain_id)
        env_name = get_environment_name(domain_id, project_name)                
        if not name:
            raise click.BadParameter(f"MWAA environment ARN not found in project '{name}'.")
        session = boto3.Session(profile_name=account, region_name='us-east-1')
        client = session.client("mwaa")
        status = wait_for_dag(client, env_name, name, run_id)
        click.echo(f"✅ DAGrun '{run_id}' status: {status}")
    except Exception as e:
        click.echo(f"❌ Error listing dags: {str(e)}", err=True)
        click.get_current_context().exit(1)


def register_commands(cli):
    """Register workflow commands with the main CLI"""
    cli.add_command(workflows)

