## Secrets Manager Aurora Rotation for an Application running inside a Fargate Container

You will need to ensure that the [AWS Serverless Application Model (SAM) Command Line Interface (CLI)](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) is installed.

[Quickstart using virtual env](https://github.com/awslabs/aws-sam-cli/issues/1266#issuecomment-510253729)

```
python3 -m venv samcli-venv
source samcli-venv/bin/activate
pip3 install --upgrade pip
pip3 install aws-sam-cli
sam --version
```

Create a AWS KMS key administrator role. Be sure that the key policy that you create allows the current user to [administer the CMK](https://aws.amazon.com/premiumsupport/knowledge-center/update-key-policy-future/).

For example, create a role named 'KeyAdministratorRole' with the following IAM Policy.

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "kms:Create*",
                "kms:Describe*",
                "kms:Enable*",
                "kms:List*",
                "kms:Put*",
                "kms:Update*",
                "kms:Revoke*",
                "kms:Disable*",
                "kms:Get*",
                "kms:Delete*",
                "kms:ScheduleKeyDeletion",
                "kms:CancelKeyDeletion",
                "kms:TagResource",
                "kms:UntagResource"
            ],
            "Resource": "*",
            "Effect": "Allow"
        }
    ]
}
```

You can also run
```
key-admin.sh 
```

You will need to create an AWS CodeCommit repository named 'django-webapp' in the primary region in order for the AWS CodePipeline to build the Docker image. You can clone this repo and push to CodeCommit in the region.

If you are familiar with editing the .git/config file, you can use these as examples and substitute the corresponding region for REGION-HERE. Install [git-remote-codecommit](https://github.com/aws/git-remote-codecommit)

```
[remote "aws"]
    url = codecommit::REGION-HERE://django-webapp
    fetch = +refs/heads/*:refs/remotes/aws/*
```

Then execute

```
git push aws main

```

Deploy using the provided script.

Update the Bucket name for the deployed resources.

The script will build the Lambda source code and generate deployment artifacts that target Lambda's execution environment.


```
cd cloudformation/scripts
./secretsmanager-multipleuser.sh
```

After successfully deploying, you will need to run the Lambda to create the application user. This will create the scoped down database application user with the main database credentials. This application user is then used by the Django web app, so that the application doesn't obtain database administrator privileges.


## License Summary

This sample code is made available under the MIT-0 license. See the LICENSE file.
