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
    click.echo("  list-domains      List domains in the current AWS account.")
    click.echo("  describe-domain   Display detailed information about a specific domain.")
    click.echo("  create-domain     Create a new domain.")
    click.echo("  delete-domain     Delete a domain and its resources (use with caution).")
    click.echo("  list-accounts     List accounts associated with a domain.")
    click.echo("  invite-account    Invite an AWS account to join domains.")
    click.echo("  describe-blueprint Display detailed information about a blueprint configuration in a domain and account.")
    click.echo("  uninvite-account  Remove an AWS account's access to domains.")
    click.echo("  list-projects     List all projects in a domain.")
    click.echo("  create-project    Create a new project in a domain.")
    click.echo("  delete-project    Delete a project from a domain.")
    