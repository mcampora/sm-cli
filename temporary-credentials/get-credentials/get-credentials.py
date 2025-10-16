#!/usr/bin/env python3
import os
import boto3
import configparser

def assume_role(role_arn, session_name, profile):
    """Assume an IAM role and return the temporary credentials."""
    if profile == 'default':
        session = boto3.Session()
    else:
        session = boto3.Session(profile_name=profile)
    client = session.client('sts')
    try:
        response = client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=session_name
        )
        return response['Credentials']
    except Exception as e:
        print(f"Error assuming role {role_arn}: {str(e)}")
        raise

def write_credentials(credentials, profile_name, credentials_file):
    """Write credentials to a file."""
    config = configparser.ConfigParser()
    if os.path.exists(credentials_file):
        config.read(credentials_file)
    
    config[profile_name] = {
        'aws_access_key_id': credentials['AccessKeyId'],
        'aws_secret_access_key': credentials['SecretAccessKey'],
        'aws_session_token': credentials['SessionToken']
    }
    
    with open(credentials_file, 'w') as f:
        config.write(f)
    print(f"Credentials saved to {profile_name} profile in {credentials_file}")

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='Collect AWS credentials by assuming roles')
    parser.add_argument('--role-arn', type=str, help='The role ARN to assume')
    parser.add_argument('--profile-name', type=str, default='default', help='The profile name to use for the credentials')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    profile = 'default'
    if args.profile_name != 'dev':
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = './credentials'
        profile = 'dev'
    if args.role_arn:
        role_creds = assume_role(
            args.role_arn,
            'assumed-session',
            profile=profile
        )
        write_credentials(role_creds, args.profile_name, './credentials')
