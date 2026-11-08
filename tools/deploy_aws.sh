#!/bin/zsh
# Creates or updates the AWS listening site (aws_site/template.yaml), then uploads the pages
# and rounds. Safe to run again: it only changes what changed.
#
# Needs the AWS command line logged in to QuranLingo's account:
#   aws configure --profile quranlingo
# Run from the TTS folder:  zsh tools/deploy_aws.sh
set -e
cd "${0:A:h}/.."
PROFILE=${AWS_PROFILE:-quranlingo}
REGION=${AWS_REGION:-eu-central-1}
STACK=quranlingo-voices
LOGIN=(--profile $PROFILE --region $REGION)

ACCOUNT=$(aws sts get-caller-identity --query Account --output text $LOGIN)
print "Account $ACCOUNT, region $REGION, stack $STACK"

# A private bucket for the Lambda code package (CloudFormation reads the code from there).
CODE_BUCKET="quranlingo-voices-code-$ACCOUNT-$REGION"
if ! aws s3api head-bucket --bucket $CODE_BUCKET $LOGIN 2>/dev/null; then
  aws s3 mb "s3://$CODE_BUCKET" $LOGIN
  aws s3api put-public-access-block --bucket $CODE_BUCKET $LOGIN --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
fi

mkdir -p outputs
aws cloudformation package --template-file aws_site/template.yaml --s3-bucket $CODE_BUCKET \
  --output-template-file outputs/aws_template_packaged.yaml $LOGIN
aws cloudformation deploy --template-file outputs/aws_template_packaged.yaml --stack-name $STACK \
  --capabilities CAPABILITY_IAM --no-fail-on-empty-changeset $LOGIN

AWS_PROFILE=$PROFILE AWS_REGION=$REGION python3 tools/aws_tools.py publish
