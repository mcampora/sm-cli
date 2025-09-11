from hashlib import file_digest
import click
import boto3
from botocore.exceptions import ClientError
import json
from dotenv import load_dotenv
from sm.commands.utils import get_domain_id, delete_resource_shares, get_resource_shares
import time

@click.command()
@click.option('--domain-id', required=False, help='The ID of the domain')
@click.option('--domain-name', help='The name of the domain (alternative to domain-id)')
def list_accounts(domain_id, domain_name):
    """List all accounts associated with a DataZone domain.
    
    Example:
        sm list-accounts --domain-id dzd_xxxxxxxxx
        sm list-accounts --domain-name my-domain
    """
    try:
        domain_id = get_domain_id(domain_name, domain_id)
        shares = get_resource_shares(domain_id)
        for share in shares:
            click.echo(f"✅ Found resource share for {share['account_id']} ({share['arn']})")

    except Exception as e:
        click.echo(f"❌ Error listing resource shares: {str(e)}", err=True)
        click.get_current_context().exit(1)


def get_profile_details(profile):
    session = boto3.Session(profile_name=profile)
    sts = session.client('sts')
    identity = sts.get_caller_identity()
    return identity


def create_role(profile, name, trust_policy, managed_policies):
    arn = None
    session = boto3.Session(profile_name=profile)
    iam = session.client('iam')
    try:
        res = iam.get_role(RoleName=name)
        arn = res['Role']['Arn']
    except ClientError as e:
        pass
    if not arn:
        res = iam.create_role(
            RoleName=name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
        )
        arn = res['Role']['Arn']
        click.echo(f"    ✅ Created role '{name}' ARN: {arn}")
    else:
        click.echo(f"    ✅ Role '{name}' already exists.")
    for policy in managed_policies:
        iam.attach_role_policy(RoleName=name, PolicyArn=policy)
    return arn


def create_access_role(profile, region, account_id, domain_id):
    name = f"AmazonSageMakerManageAccess-{region}-{domain_id}"
    trust_policy = {
        "Version": "2012-10-17", 
        "Statement": [ 
            { 
                "Effect": "Allow", 
                "Principal": { 
                    "Service": "datazone.amazonaws.com" 
                }, 
                "Action": "sts:AssumeRole", 
                "Condition": { 
                    "StringEquals": { 
                        "aws:SourceAccount": account_id
                    },
                    "ArnEquals": { 
                        "aws:SourceArn": f"arn:aws:datazone:{region}:{account_id}:domain/{domain_id}"
                    }
                }
            }
        ]
    }
    managed_policies = [ 
        "arn:aws:iam::aws:policy/service-role/AmazonDataZoneGlueManageAccessRolePolicy",
        "arn:aws:iam::aws:policy/AmazonDataZoneSageMakerManageAccessRolePolicy",
        "arn:aws:iam::aws:policy/service-role/AmazonDataZoneRedshiftManageAccessRolePolicy" 
    ]
    return create_role(profile, name, trust_policy, managed_policies)


def create_provisioning_role(profile, account_id):
    name = f"AmazonSageMakerProvisioning-{account_id}"
    trust_policy = { 
        "Version": "2012-10-17", 
        "Statement": [ 
            { 
                "Effect": "Allow", 
                "Principal": { 
                    "Service": "datazone.amazonaws.com" 
                }, 
                "Action": "sts:AssumeRole", 
                "Condition": { 
                    "StringEquals": { 
                        "aws:SourceAccount": account_id 
                    }
                }
            }
        ]
    }
    managed_policies = [ "arn:aws:iam::aws:policy/service-role/SageMakerStudioProjectProvisioningRolePolicy" ]
    return create_role(profile, name, trust_policy, managed_policies)
            

def put_environment_blueprint_configuration(datazone, domain_id, blueprint_id, region, access_role_arn, provisioning_role_arn):
    datazone.put_environment_blueprint_configuration(
        domainIdentifier=domain_id, 
        environmentBlueprintIdentifier=blueprint_id, 
        enabledRegions=[region], 
        manageAccessRoleArn=access_role_arn, 
        provisioningRoleArn=provisioning_role_arn
    )


def add_policy_grant(datazone, domain_id, invitee_account_id, blueprint_id):
    domain = datazone.get_domain(identifier=domain_id)
    root_domain_unit_id = domain['rootDomainUnitId']
    datazone.add_policy_grant(
        detail={"createEnvironmentFromBlueprint":{}},
        domainIdentifier=domain_id,
        entityType='ENVIRONMENT_BLUEPRINT_CONFIGURATION',
        entityIdentifier=f"{invitee_account_id}:{blueprint_id}",
        policyType='CREATE_ENVIRONMENT_FROM_BLUEPRINT',
        principal={"project":{"projectDesignation":"CONTRIBUTOR","projectGrantFilter":{"domainUnitFilter":{"domainUnit":f"{root_domain_unit_id}","includeChildDomainUnits":True}}}}
    )   


def configure_workflow_blueprint(profile, invitee_account_id, domain_id, region, access_role_arn, provisioning_role_arn):
    session = boto3.Session(profile_name=profile, region_name=region)
    datazone = session.client('datazone')
    workflow_id = datazone.list_environment_blueprints(domainIdentifier=domain_id, managed=True, name='Workflow')['items'][0]['id']
    put_environment_blueprint_configuration(datazone, domain_id, workflow_id, region, access_role_arn, provisioning_role_arn)
    add_policy_grant(datazone, domain_id, invitee_account_id, workflow_id)
    click.echo(f"    ✅ Configured Workflow blueprint {workflow_id}.")


def configure_datalake_blueprint(profile, invitee_account_id, domain_id, region, access_role_arn, provisioning_role_arn):
    session = boto3.Session(profile_name=profile, region_name=region)
    datazone = session.client('datazone')
    datalake_id = datazone.list_environment_blueprints(domainIdentifier=domain_id, managed=True, name='DataLake')['items'][0]['id']
    put_environment_blueprint_configuration(datazone, domain_id, datalake_id, region, access_role_arn, provisioning_role_arn)
    add_policy_grant(datazone, domain_id, invitee_account_id, datalake_id)
    click.echo(f"    ✅ Configured DataLake/LakeHouseDatabase blueprint {datalake_id}.")
    

def configure_tooling_blueprint(profile, invitee_account_id, domain_id, region, access_role_arn, provisioning_role_arn):
    session = boto3.Session(profile_name=profile, region_name=region)
    datazone = session.client('datazone')
    tooling_id = datazone.list_environment_blueprints(domainIdentifier=domain_id, managed=True, name='Tooling')['items'][0]['id']

    # need an S3 bucket
    domain_s3_bucket_prefix = f"amazon-sagemaker-{invitee_account_id}-{region}"
    domain_s3_bucket = session.client('s3').list_buckets(Prefix=domain_s3_bucket_prefix)['Buckets'][0]['Name']
    if domain_s3_bucket == "null":
        domain_s3_bucket = domain_s3_bucket_prefix
        session.client('s3').create_bucket(Bucket=domain_s3_bucket, CreateBucketConfiguration={'LocationConstraint': region})
        click.echo(f"        ✅ Created S3 bucket {domain_s3_bucket}.")
    else:
        click.echo(f"        ✅ The S3 bucket {domain_s3_bucket} already exists!")

    # need a VPC
    # When I have the choice I'm using a specific rule which might not work everywhere
    # I'm looking for the first VPC with a tag "Name" starting with "golden"
    ec2 = session.client('ec2')
    vpc_id = None
    vpcs = ec2.describe_vpcs()['Vpcs']
    if len(vpcs) == 1:
        vpc_id = vpcs[0]['VpcId']
    else:
        for vpc in vpcs:
            for tag in vpc['Tags']:
                if tag['Key'] == 'Name' and tag['Value'].startswith('golden'):
                    vpc_id = vpc['VpcId']
                    break
    click.echo(f"        ✅ Selected VPC: {vpc_id}")
    
    # need 3 subnets /AZs
    subnets = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['Subnets']
    ids = []
    azs = []
    for s in subnets:
        # get the subnet name
        subnet_name = None
        for tag in s['Tags']:
            if tag['Key'] == 'Name':
                subnet_name = tag['Value']
                break
        subnet_id = s['SubnetId']
        az_id = s['AvailabilityZoneId']
        if subnet_name and subnet_name.startswith('private'):
            ids.append(subnet_id)
            azs.append(az_id)
        if len(ids) == 3:
            break
    click.echo(f"        ✅ Selected subnets: {ids}")
    click.echo(f"        ✅ Selected AZs: {azs}")
    
    datazone.put_environment_blueprint_configuration(
        domainIdentifier=domain_id, 
        environmentBlueprintIdentifier=tooling_id, 
        enabledRegions=[region], 
        manageAccessRoleArn=access_role_arn, 
        provisioningRoleArn=provisioning_role_arn,
        regionalParameters={
            region: {
                "AZs": f"{','.join(azs)}",
                "S3Location": f"s3://{domain_s3_bucket}",
                "Subnets": f"{','.join(ids)}",
                "VpcId": f"{vpc_id}"
            }
        }
    )
    add_policy_grant(datazone, domain_id, invitee_account_id, tooling_id)
    click.echo(f"    ✅ Configured Tooling blueprint {tooling_id}.")


def configure_blueprints(profile, invitee_account_id, governance_account_id, domain_id, region):
    access_role_arn = create_access_role(profile, region, governance_account_id, domain_id)
    provisioning_role_arn = create_provisioning_role(profile, governance_account_id)

    configure_workflow_blueprint(profile, invitee_account_id, domain_id, region, access_role_arn, provisioning_role_arn)
    configure_datalake_blueprint(profile, invitee_account_id, domain_id, region, access_role_arn, provisioning_role_arn)
    configure_tooling_blueprint(profile, invitee_account_id, domain_id, region, access_role_arn, provisioning_role_arn) 


def create_project_profile(profile, region, invitee_account_id, governance_account_id, domain_id):
    session = boto3.Session(profile_name=profile, region_name=region)
    datazone = session.client('datazone')
    tooling_id = datazone.list_environment_blueprints(domainIdentifier=domain_id, managed=True, name='Tooling')['items'][0]['id']
    datalake_id = datazone.list_environment_blueprints(domainIdentifier=domain_id, managed=True, name='DataLake')['items'][0]['id']
    workflow_id = datazone.list_environment_blueprints(domainIdentifier=domain_id, managed=True, name='Workflow')['items'][0]['id']
    
    with open('./templates/project-profile-template.json', 'r') as f:
        template = f.read()
    template = template.replace('${AWS_REGION}', region)
    template = template.replace('${TOOLING_ID}', tooling_id)
    template = template.replace('${DATALAKE_ID}', datalake_id)
    template = template.replace('${WORKFLOW_ID}', workflow_id)
    template = template.replace('${ACCOUNT_ID}', invitee_account_id)
    config = json.loads(template)
    #click.echo(config)

    # will check that a project profile SQL Analytics does not already exist in the provided domain
    datazone = boto3.client('datazone')
    profile_name = f'SQLAnalytics_{profile}'
    profiles = datazone.list_project_profiles(domainIdentifier=domain_id, name=profile_name)['items']
    for profile in profiles:
        if profile['name'] == profile_name:
            click.echo(f"    ✅ The project profile {profile_name} already exists in the domain {domain_id}.")
            return

    project_profile_id = datazone.create_project_profile(
        domainIdentifier=domain_id,
        name=profile_name,
        description=f"Default project profile offering access to Athena in the {invitee_account_id} account.",
        status="ENABLED",
        environmentConfigurations=config
    )['id']
    domain = datazone.get_domain(identifier=domain_id)
    root_domain_unit_id = domain['rootDomainUnitId']
    datazone.add_policy_grant(
        detail={"createProjectFromProjectProfile":{"projectProfiles":[f"{project_profile_id}"],"includeChildDomainUnits":True}},
        domainIdentifier=domain_id,
        entityType="DOMAIN_UNIT",
        entityIdentifier=root_domain_unit_id,
        policyType="CREATE_PROJECT_FROM_PROJECT_PROFILE",
        principal={"user":{"allUsersGrantFilter":{}}}
    )
    click.echo(f"    ✅ Created project profile {profile_name} in the domain {domain_id}.")


@click.command()
@click.option('--domain-id', required=False, help='Domain ID to invite the account to (optional)')
@click.option('--domain-name', required=False, help='Domain name to invite the account to (alternative to domain-id)')
@click.option('--profile', required=True, help='AWS profile to invite')
def invite_account(domain_id, domain_name, profile):
    """Invite an AWS account to join DataZone domains.
    
    This command helps manage AWS account invitations to DataZone domains.
    
    Example:
        sm invite-account --domain-name marc_test --profile dev
    """
    try:
        domain_id = get_domain_id(domain_name, domain_id)
        region = 'us-east-1'

        # load the credentials and id of the invited account
        invitee_identity = get_profile_details(profile)
        invitee_account_id = invitee_identity['Account']

        # create the ram resource share in the governance account
        governance_identity = get_profile_details('default')
        governance_account_id = governance_identity['Account']
        ram = boto3.client('ram')
        ram.create_resource_share(
            name=f"DataZone-EXTENDED_ACCESS-{domain_id}-ORG-ONLY",
            principals=[invitee_account_id],
            resourceArns=[f'arn:aws:datazone:{region}:{governance_account_id}:domain/{domain_id}'],
            permissionArns=["arn:aws:ram::aws:permission/AWSRAMPermissionsAmazonDatazoneDomainExtendedServiceAccess"],
            allowExternalPrincipals=False
        )
        click.echo(f"    ✅ Configured resource share for {invitee_account_id}, wait for the domain share to be ready...")
        time.sleep(15)

        # configure blueprints in the invited account
        configure_blueprints(profile, invitee_account_id, governance_account_id, domain_id, region)

        # configure a project profile in the governance account
        create_project_profile(profile, region, invitee_account_id, governance_account_id, domain_id)

        click.echo(f"✅ Account {profile} ({invitee_account_id}) joined the domain {domain_name} ({domain_id}).")

    except Exception as e:
        click.echo(f"❌ Error processing account invitation: {str(e)}", err=True)
        click.get_current_context().exit(1)


def delete_project_profile(profile, domain_id):
    datazone = boto3.client('datazone')
    profiles = datazone.list_project_profiles(domainIdentifier=domain_id, name=f'SQLAnalytics_{profile}')['items']
    #click.echo(profiles)
    for p in profiles:
        if p['name'] == f'SQLAnalytics_{profile}':
            projects = datazone.list_projects(domainIdentifier=domain_id)['items']
            for project in projects:
                project_detail = datazone.get_project(domainIdentifier=domain_id, identifier=project['id'])
                #click.echo(project_detail)
                click.echo(project)
                if project_detail['projectProfileId'] == p['id']:
                    datazone.delete_project(domainIdentifier=domain_id, identifier=project['id'], skipDeletionCheck=True)
                    click.echo(f"    ✅ Deleted project {project['name']} in the domain {domain_id}.")
            datazone.delete_project_profile(domainIdentifier=domain_id, identifier=p['id'])
            click.echo(f"    ✅ Deleted project profile {p['name']} in the domain {domain_id}.")


@click.command()
@click.option('--domain-id', required=False, help='Domain ID to uninvite the account from (optional)')
@click.option('--domain-name', required=False, help='Domain name to uninvite the account from (alternative to domain-id)')
@click.option('--profile', required=True, help='AWS profile to uninvite')
def uninvite_account(domain_id, domain_name, profile):
    """Uninvite an AWS account from DataZone domains by removing its resource shares.
    
    This command removes the resource shares that grant the specified account access to the domain.
    
    Example:
        sm uninvite-account --domain-name marc_test --profile dev
    """
    try:
        domain_id = get_domain_id(domain_name, domain_id)

        invitee_identity = get_profile_details(profile)
        invitee_account_id = invitee_identity['Account']

        # delete the project profile associated with the account
        delete_project_profile(profile, domain_id)

        #delete the resource share associated with the account
        delete_resource_shares(domain_id, invitee_account_id)

        click.echo(f"✅ Account {profile} ({invitee_account_id}) uninvited from the domain {domain_name} ({domain_id}).")

    except Exception as e:
        click.echo(f"❌ Error uninviting account: {str(e)}", err=True)
        click.get_current_context().exit(1)
