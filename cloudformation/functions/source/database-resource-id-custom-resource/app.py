from __future__ import print_function
from crhelper import CfnResource
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialise the helper, all inputs are optional, this example shows the defaults
helper = CfnResource(json_logging=False, log_level='DEBUG', boto_level='CRITICAL')

#import cfnresponse
import boto3
rds = boto3.client('rds')

@helper.create
def create(event, context):
    logger.info(f"Got Create {event}")
    # Optionally return an ID that will be used for the resource PhysicalResourceId, 
    # if None is returned an ID will be generated. If a poll_create function is defined 
    # return value is placed into the poll event as event['CrHelperData']['PhysicalResourceId']
    #
    # To add response data update the helper.Data dict
    # If poll is enabled data is placed into poll event as event['CrHelperData']
    database_resource_id=None
    if 'DBClusterIdentifier' in event['ResourceProperties']:
        logger.info("cluster type")
        response = rds.describe_db_clusters(
                DBClusterIdentifier=event['ResourceProperties']['DBClusterIdentifier']
        )
        database_resource_id=response['DBClusters'][0]['DbClusterResourceId']
    else:
        logger.info("instance type")
        response = rds.describe_db_instances(
            DBInstanceIdentifier=event['ResourceProperties']['DatabaseInstanceId']
        )
        database_resource_id=response["DBInstances"][0]["DbiResourceId"]

    logger.info("DbiResourceId={}".format(database_resource_id))
    helper.Data.update({"DbiResourceId": database_resource_id})
    return None


@helper.update
def update(event, context):
    logger.info("Got Update")
    # If the update resulted in a new resource being created, return an id for the new resource. CloudFormation will send
    # a delete event with the old id when stack update completes


@helper.delete
def delete(event, context):
    logger.info("Got Delete")
    # Delete never returns anything. Should not fail if the underlying resources are already deleted. Desired state.


def lambda_handler(event, context):
    logger.info("DBI Custom Resource")
    helper(event, context)


