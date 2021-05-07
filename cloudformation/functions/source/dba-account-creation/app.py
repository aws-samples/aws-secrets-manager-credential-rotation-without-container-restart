#https://docs.aws.amazon.com/code-samples/latest/catalog/python-secretsmanager-secrets_manager.py.html
from __future__ import print_function
from crhelper import CfnResource

import os
import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

import pymysql

import boto3
secretsmanager = boto3.client('secretsmanager')

import json

helper = CfnResource(json_logging=False, log_level='DEBUG', boto_level='CRITICAL', sleep_on_delete=120)

#rds settings
#DatabaseEndpointURL
rds_host  = os.environ["DatabaseEndpointURL"]
#DatabaseCredentialsSecretsArn
get_secret_value_response = secretsmanager.get_secret_value(
    SecretId=os.environ["DatabaseCredentialsSecretsArn"],
)
credentials=json.loads(get_secret_value_response["SecretString"])
name = credentials["username"]
password = credentials["password"]

#Please specify the region certificate to ensure that the connection is to the intended region. For now using the combined certificate bundle.
#Certificates available from here https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.SSL.html#UsingWithRDS.SSL.IntermediateCertificates
s3 = boto3.client('s3')
certificate_file='rds-combined-ca-bundle.pem'
certificate_full_path=os.path.join('/tmp',certificate_file)
s3.download_file('rds-downloads', 'rds-combined-ca-bundle.pem', certificate_full_path)

try:
    conn = pymysql.connect(host=rds_host, user=name, password=password, connect_timeout=5, ssl={'ca':certificate_full_path})
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")
except Exception as e:
    logger.exception("ERROR: Unexpected error: Could not connect to MySQL instance.")
    #sys.exit()
    helper.init_failure(e)

@helper.create
def create(event, context):
    logger.info(f"Got Create {event}")
    with conn.cursor() as cursor:
        cursor.execute("CREATE USER sample_dba IDENTIFIED WITH AWSAuthenticationPlugin as 'RDS';")
        print(cursor.fetchone())
        cursor.execute("GRANT USAGE ON *.* TO 'sample_dba'@'%' REQUIRE SSL;")
        print(cursor.fetchone())
        cursor.execute("FLUSH PRIVILEGES;")
        print(cursor.fetchone())
    
    return None


@helper.update
def update(event, context):
    logger.info("Got Update")
    # If the update resulted in a new resource being created, return an id for the new resource. 
    # CloudFormation will send a delete event with the old id when stack update completes


@helper.delete
def delete(event, context):
    logger.info("Got Delete")
    # Delete never returns anything. Should not fail if the underlying resources are already deleted.
    # Desired state.

def lambda_handler(event, context):
    helper(event, context)

