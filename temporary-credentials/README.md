# Helper scripts

## collect temporary credentials from assumed roles

The script accepts the arn of a role and a profile name as parameters.  
It assumes the role, get temporary credentials, save them under the profile name in a credentials file locally.  
> python3 collect-credentials.py <arn> <profile_name>

## provision roles in different accounts

These scripts are used to provision GH runners roles in different accounts (dev, governance, test, prod)
> ./provision-roles.sh

At the end of the script, it will create a `SM-<profile>-Role.arn` file in the same directory as the script.  
