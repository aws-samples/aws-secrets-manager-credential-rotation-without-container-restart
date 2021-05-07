from __future__ import print_function
from crhelper import CfnResource

import sys
import os
from contextlib import closing

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

import boto3
secretsmanager = boto3.client('secretsmanager')

secret_id = os.environ["ApplicationUserSecretsManagerArn"]
master_secret_id = os.environ["MasterUserSecretsManagerArn"]

import pymysql
import json

helper = CfnResource(json_logging=False, log_level='DEBUG', boto_level='CRITICAL', sleep_on_delete=120)

@helper.create
def create(event, context):
    logger.info(f"Got Create {event}")
   
    create_application_user()
    connect_as_application_user()
 
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

def create_application_user():
    master_secret_value=secretsmanager.get_secret_value(SecretId=master_secret_id)
    master_secret=json.loads(master_secret_value["SecretString"])
    master_username=master_secret["username"]
    master_password=master_secret["password"]
    rds_host=master_secret["host"]

    print(rds_host)
    conn = pymysql.connect(host=rds_host, user=master_username, password=master_password, connect_timeout=5)
    
    secret_value=secretsmanager.get_secret_value(SecretId=secret_id)
    secret=json.loads(secret_value["SecretString"])
    username=secret["username"]
    password=secret["password"]

    with conn.cursor() as cursor:
        create_query=f"CREATE USER \'{username}\' IDENTIFIED BY \"{password}\""
        cursor.execute(create_query)
        print(cursor.fetchone())
        
        #GRANT ALL PRIVILEGES ON database_name.* TO 'username'@'localhost';
        #GRANT SELECT, INSERT, DELETE ON database TO username@'localhost' IDENTIFIED BY 'password';
        grant_query=f"GRANT USAGE ON *.* TO \'{username}\'@'%' IDENTIFIED BY \"{password}\""
        cursor.execute(grant_query)
        print(cursor.fetchone())
        
        grant_query=f"GRANT INDEX, REFERENCES, ALTER, CREATE, SELECT, INSERT, DELETE ON *.* TO \'{username}\'@'%' IDENTIFIED BY \"{password}\""
        cursor.execute(grant_query)
        print(cursor.fetchone())        
        
        cursor.execute("FLUSH PRIVILEGES;")
        print(cursor.fetchone())
        
    print("created application user")
        
def connect_as_application_user():
    secret_value=secretsmanager.get_secret_value(SecretId=secret_id)
    secret=json.loads(secret_value["SecretString"])
    username=secret["username"]
    password=secret["password"]
    dbname=secret["dbname"]
    rds_host=secret["host"]

    conn = pymysql.connect(host=rds_host, user=username, password=password, connect_timeout=5, db=dbname)
    with conn.cursor() as cursor:
        cursor.execute("SELECT 1;")
        print(cursor.fetchone())
        
        cursor.execute("SELECT 1;")
        print(cursor.fetchone())
        
    print("connected as application user")

