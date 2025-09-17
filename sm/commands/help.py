import click

@click.command()
def help():
    """Show this help message and exit."""
    # This is a custom help message. Click's default help is still available with --help.
    click.echo("SM - SageMaker Unified Studio CLI Tool.")
    click.echo("\nUsage:")
    click.echo("  sm [OPTIONS] COMMAND [ARGS]...\n")
    click.echo("Options:")
    click.echo("  --help     Show this message and exit.")
    click.echo("  --version  Show the version and exit.\n")
    click.echo("Commands:")
    click.echo("  help              Show this help message and exit.")
    click.echo("  status            Check AWS connection status.")
    click.echo("  domains           Manage DataZone domains")
    click.echo("  accounts          Manage AWS accounts in DataZone domains")
    click.echo("  projects          Manage DataZone projects")
    
    click.echo("\nDomains Commands:")
    click.echo("  domains list      List domains in the current AWS account.")
    click.echo("  domains describe  Display detailed information about a specific domain.")
    click.echo("  domains create    Create a new domain.")
    click.echo("  domains delete    Delete a domain and its resources (use with caution).")
    
    click.echo("\nAccounts Commands:")
    click.echo("  accounts list            List accounts in a domain.")
    click.echo("  accounts invite          Invite an AWS account to a domain.")
    click.echo("  accounts uninvite        Remove an account from a domain.")
    click.echo("  accounts list-blueprints List blueprints in a domain.")
    click.echo("  accounts describe-blueprint Show details of a specific blueprint.")
    
    click.echo("\nProjects Commands:")
    click.echo("  projects list      List projects in a domain.")
    click.echo("  projects create    Create a new project in a domain.")
    click.echo("  projects delete    Delete a project from a domain.")
    