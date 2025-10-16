# Provision roles
A script used to provision a build role in each account participating to the CI/CD workflow.  

You have to create a credential file named `credentials` in the same directory as the script.  
This file should contain a [governance], [dev], [test], [prod] profiles with the appropriate tokens (access key id, secret access key, session token) to access each account and create the required resources.  

Launch `provision-roles.sh` it deploys the template in each account using the profile name to differentiate the resources (ex. SM-<profile>-Role, SM-<profile>-Stack).  
At the end of the script, it will create a `SM-<profile>-Role.arn` file in the same directory as the script.  

My CodeBuild project is in the dev account, so the dev role will act as authority to assume the other roles.
The dev role trusts the Innovation role in the dev account.
The test, prod and governance roles trust the dev role in the dev account.
