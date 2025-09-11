import click
import os
import boto3

from sm.commands.help import help as help_command
from sm.commands.status import status as status_command
from sm.commands.domains import (
    list_domains as list_domains_command,
    describe_domain as describe_domain_command,
    create_domain as create_domain_command,
    delete_domain as delete_domain_command
)
from sm.commands.accounts import (
    list_accounts as list_accounts_command,
    invite_account as invite_account_command,
    uninvite_account as uninvite_account_command
)
from sm.commands.projects import (
    list_projects as list_projects_command,
    create_project as create_project_command
)

@click.group()
@click.version_option()
def main():
    """SM Setup - AWS Resource Management CLI Tool."""

    # Load environment variables from .env file if it exists
    # by default the commands are executed against the gov account

    # some commands require access to a remote account, 
    # for instance when you want to connect this account to a domain and prepare this account to host a project environment
    # the specific env file will be provided as an option and loaded in the context of the command
    
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = './credentials'
    boto3.setup_default_session(profile_name='default')


    # Verify AWS credentials are set
    #if not all([os.getenv('AWS_ACCESS_KEY_ID'), os.getenv('AWS_SECRET_ACCESS_KEY')]):
    #    click.echo("Error: AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in your environment or .env file.", err=True)
    #    click.get_current_context().exit(1)

main.add_command(help_command, name='help')
main.add_command(status_command, name='status')
main.add_command(list_domains_command, name='list-domains')
main.add_command(describe_domain_command, name='describe-domain')
main.add_command(create_domain_command, name='create-domain')
main.add_command(delete_domain_command, name='delete-domain')
main.add_command(list_accounts_command, name='list-accounts')
main.add_command(invite_account_command, name='invite-account')
main.add_command(uninvite_account_command, name='uninvite-account')
main.add_command(list_projects_command, name='list-projects')
main.add_command(create_project_command, name='create-project')

if __name__ == "__main__":
    main()
