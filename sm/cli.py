import click
import os
import boto3
from sm.commands.help import help as help_command
from sm.commands.status import status as status_command
from sm.commands.domains import register_commands as register_domains_commands
from sm.commands.accounts import register_commands as register_accounts_commands
from sm.commands.projects import register_commands as register_projects_commands
from sm.commands.workflows import register_commands as register_workflows_commands
from sm.commands.assets import register_commands as register_assets_commands

@click.group()
@click.version_option()
def main():
    """SM Setup - AWS Resource Management CLI Tool."""
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = './credentials'
    boto3.setup_default_session(profile_name='default', region_name='us-east-1')

# Register command groups
register_domains_commands(main)
register_accounts_commands(main)
register_projects_commands(main)
register_workflows_commands(main)
register_assets_commands(main)

# Register individual commands
main.add_command(help_command, name='help')
main.add_command(status_command, name='status')

if __name__ == "__main__":
    main()
