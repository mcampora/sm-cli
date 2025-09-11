import boto3
import click


def get_domain_id(domain_name, domain_id) -> str:
    if domain_name and not domain_id:
        datazone = boto3.client('datazone')
        domains = datazone.list_domains()['items']
        for domain in domains:
            if domain['name'] == domain_name:
                domain_id = domain['id']
                break
        if not domain_id:
            raise click.ClickException(f"Domain '{domain_name}' not found.")
    if not domain_id:
        raise click.ClickException("Please provide either --domain-id or --domain-name")
    return domain_id


def get_resource_shares(domain_id):
    """Get the resource shares for a specific DataZone domain."""
    result = []
    ram = boto3.client('ram')
    shares = ram.get_resource_shares(resourceOwner='SELF')['resourceShares']
    for share in shares:
        if share['name'].startswith(f"DataZone-EXTENDED_ACCESS-{domain_id}-ORG-ONLY"):
            #click.echo(f"✅ Found resource share for {share}")
            status = share['status']
            if status != 'DELETED':
                arn = share['resourceShareArn']
                details = ram.get_resource_share_associations(resourceShareArns=[arn], associationType='PRINCIPAL')
                account_id = details['resourceShareAssociations'][0]['associatedEntity']
                result.append({ 'account_id': account_id, 'arn': arn, 'status': status })
    return result
    

def delete_resource_shares(domain_id, account_id = None):
    ram = boto3.client('ram')
    shares = get_resource_shares(domain_id)
    for share in shares:
        to_delete = True
        if account_id != None and share['account_id'] != account_id:
            to_delete = False
        if to_delete:
            ram.delete_resource_share(resourceShareArn=share['arn'])
            click.echo(f"    ✅ Deleted resource share {share['arn']}.")
    
