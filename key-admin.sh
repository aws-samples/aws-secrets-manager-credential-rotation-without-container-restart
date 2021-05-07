#!/bin/bash
set -Eeuox pipefail

STACK_NAME=KeyAdministratorStack
TEMPLATE=key-administrator-role.yaml

aws cloudformation validate-template --template-body file://"$TEMPLATE"

aws cloudformation create-stack \
    --stack-name "$STACK_NAME" \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
    --template-body file://"$TEMPLATE"

