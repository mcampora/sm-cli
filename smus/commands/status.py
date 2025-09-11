import click
import boto3
import os

@click.command()
@click.option('--profile', 'profile', required=False, help='The profile to use for AWS credentials')
def status(profile):
    """Check AWS connection status."""
    try:
        click.echo("Checking AWS connection status...")
        if not profile:
            profile = "default"
        session = boto3.Session(profile_name=profile)
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        click.echo("✅ Successfully connected to AWS")
        click.echo(f"Account: {identity['Account']}")
        click.echo(f"User ARN: {identity['Arn']}")
    except Exception as e:
        click.echo(f"❌ Failed to connect to AWS: {str(e)}", err=True)
        click.get_current_context().exit(1)
