import click

@click.command()
def help():
    """Show this help message and exit."""
    # This is a custom help message. Click's default help is still available with --help.
    click.echo("SMUS Setup - AWS Resource Management")
    click.echo("\nUsage:")
    click.echo("  smus [OPTIONS] COMMAND [ARGS]...\n")
    click.echo("Options:")
    click.echo("  --help     Show this message and exit.")
    click.echo("  --version  Show the version and exit.\n")
    click.echo("Commands:")
    click.echo("  help              Show this help message and exit.")
    click.echo("  status            Check AWS connection status.")
    click.echo("  list-domains      List DataZone domains in the current AWS account.")
    click.echo("  describe-domain   Display detailed information about a specific domain.")
    click.echo("  create-domain     Create a new DataZone domain.")
    click.echo("  delete-domain     Delete a DataZone domain and its resources (use with caution).")
    click.echo("  list-accounts     List accounts associated with a DataZone domain.")
    click.echo("  invite-account    Invite an AWS account to join DataZone domains.")
    click.echo("  uninvite-account  Remove an AWS account's access to DataZone domains.")
