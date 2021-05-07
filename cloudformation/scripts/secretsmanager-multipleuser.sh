#!/bin/bash
set -Eeuox pipefail

AWS_ACCOUNT=$(aws sts get-caller-identity | jq .Account -r)
BUCKET=secretsmanager-container-demo-1-${AWS_ACCOUNT}-${AWS_REGION}
STACK_NAME=secretsmanager-demo-1
TEMPLATE=cfn.secretsmanagermultipleuser.yaml

if [[ -z $(aws s3api head-bucket --bucket ${BUCKET} 2>&1) ]]; then
  echo "${BUCKET} already exists"
else
  echo "Creating ${BUCKET} as it doesn't exist"
  aws s3 mb s3://${BUCKET}
  aws s3api put-public-access-block \
    --bucket ${BUCKET} \
    --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
fi

pushd ../templates

aws cloudformation validate-template --template-body file://"$TEMPLATE"

sam build --region ${AWS_REGION} --use-container --template cfn.iamauthentication.yaml --build-dir ../tmp/iamauthentication-build-dir
sam build --region ${AWS_REGION} --use-container --template cfn.fargate.yaml --build-dir ../tmp/fargate-build-dir
sam build --region ${AWS_REGION} --use-container --template cfn.database-application-user.yaml --build-dir ../tmp/database-application-user-build-dir
sam build --region ${AWS_REGION} --use-container --template "$TEMPLATE" --build-dir ../tmp/client-side-encryption-build-dir

sam package \
    --region ${AWS_REGION} \
    --s3-bucket "$BUCKET" \
    --output-template-file ../tmp/packaged-"$TEMPLATE" \
    --template-file ../tmp/client-side-encryption-build-dir/template.yaml

aws cloudformation validate-template --template-body file://../tmp/packaged-"$TEMPLATE"

#sam deploy \
#    --stack-name "$STACK_NAME" \
#    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
#    --template-file ../tmp/packaged-"$TEMPLATE"

aws cloudformation create-stack \
    --stack-name "$STACK_NAME" \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
    --template-body file://../tmp/packaged-"$TEMPLATE" \
    --on-failure DO_NOTHING

popd
