#!/bin/bash

if [ $# -ne 3 ]; then
  echo "Usage: $0 <stack-name> <role-name> <trusted-role-arn>"
  echo ""
  exit 1
fi

STACK_NAME="$1"
ROLE_NAME="$2"
TRUSTED_ROLE_ARN="$3"

# Deploy the stack
echo "Deploying CloudFormation stack: ${STACK_NAME}, role: ${ROLE_NAME}, trusted role: ${TRUSTED_ROLE_ARN}"
#aws sts get-caller-identity --profile ${AWS_PROFILE}

aws cloudformation deploy \
  --stack-name "${STACK_NAME}" \
  --template-file role-template.yaml \
  --parameter-overrides \
    RoleName="${ROLE_NAME}" \
    TrustedRoleArn="${TRUSTED_ROLE_ARN}" \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1 \
  --profile ${AWS_PROFILE}

if [ $? -eq 0 ]; then
  ROLE_ARN=$( aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --query 'Stacks[0].Outputs[?OutputKey==`RoleArn`].OutputValue' \
    --output text \
    --region us-east-1 \
    --profile ${AWS_PROFILE} )  
  echo ${ROLE_ARN} > ${ROLE_NAME}.arn
else
  echo ""
  echo "Stack creation/update failed or timed out. Check the AWS Console for details."
fi

echo ""
