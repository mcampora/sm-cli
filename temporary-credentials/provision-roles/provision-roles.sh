#!/bin/bash

# Wrapper script to deploy the assume role with specific parameters

# Set AWS credentials and config
#export AWS_CONFIG_FILE=./config.ini
export AWS_SHARED_CREDENTIALS_FILE=./credentials

# Configuration for the dev account
export AWS_PROFILE=dev
TRUSTED_ROLE_ARN="arn:aws:iam::951479533181:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_InnovationSandboxPowerUser_ff37e6655529c2ef"
TRUSTED_ROLE_ARN="arn:aws:iam::951479533181:role/service-role/codebuild-test_custom_repo-service-role"
STACK_NAME="SM-${AWS_PROFILE}-Stack"
ROLE_NAME="SM-${AWS_PROFILE}-Role"
./provision-role.sh "${STACK_NAME}" "${ROLE_NAME}" "${TRUSTED_ROLE_ARN}"

# Configuration for the governance account
export AWS_PROFILE=governance
TRUSTED_ROLE_ARN=$( cat SM-dev-Role.arn )
STACK_NAME="SM-${AWS_PROFILE}-Stack"
ROLE_NAME="SM-${AWS_PROFILE}-Role"
./provision-role.sh "${STACK_NAME}" "${ROLE_NAME}" "${TRUSTED_ROLE_ARN}"

# Configuration for the test account
export AWS_PROFILE=test
TRUSTED_ROLE_ARN=$( cat SM-dev-Role.arn )
STACK_NAME="SM-${AWS_PROFILE}-Stack"
ROLE_NAME="SM-${AWS_PROFILE}-Role"
./provision-role.sh "${STACK_NAME}" "${ROLE_NAME}" "${TRUSTED_ROLE_ARN}"

# Configuration for the prod account
export AWS_PROFILE=prod
TRUSTED_ROLE_ARN=$( cat SM-dev-Role.arn )
STACK_NAME="SM-${AWS_PROFILE}-Stack"
ROLE_NAME="SM-${AWS_PROFILE}-Role"
./provision-role.sh "${STACK_NAME}" "${ROLE_NAME}" "${TRUSTED_ROLE_ARN}"
