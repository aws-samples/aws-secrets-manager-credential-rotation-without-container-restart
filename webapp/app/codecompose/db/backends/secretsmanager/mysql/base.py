import logging
logger = logging.getLogger(__name__)

import botocore
import botocore.session
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig

from django.db.backends.mysql import base
from django.db import DEFAULT_DB_ALIAS

import MySQLdb

import json

from codecompose.settings import DATABASE_SECRETSMANAGER_ARN

class DatabaseCredentials:
    def __init__(self):
        logger.info("init secrets manager database credentials")
        client = botocore.session.get_session().create_client('secretsmanager')
        cache_config = SecretCacheConfig()
        self.cache_secrets_manager = SecretCache(config=cache_config, client=client)
        self.secret_id=DATABASE_SECRETSMANAGER_ARN

    def get_conn_params_from_secrets_manager(self, conn_params):
        secret_json=self.cache_secrets_manager.get_secret_string(self.secret_id)
        secret_dict=json.loads(secret_json)
        username=secret_dict["username"]
        password=secret_dict["password"]
        conn_params['user']=username
        conn_params['passwd']=password
        logger.info(f"***DEMO PURPOSES ONLY*** user={username}")
        return

    def refresh_now(self):
        secret_cache_item=self.cache_secrets_manager._get_cached_secret(self.secret_id)
        secret_cache_item._refresh_needed=True
        secret_cache_item._execute_refresh()

databasecredentials=DatabaseCredentials()

class DatabaseWrapper(base.DatabaseWrapper):
    def get_new_connection(self, conn_params):
        try:
            logger.info("get connection")
            databasecredentials.get_conn_params_from_secrets_manager(conn_params)
            conn =super(DatabaseWrapper,self).get_new_connection(conn_params)
            return conn
        except MySQLdb.OperationalError as e:
            error_code=e.args[0]
            if error_code!=1045:
                raise e

            logger.info("Authentication error. Going to refresh secret and try again.")
            databasecredentials.refresh_now()
            databasecredentials.get_conn_params_from_secrets_manager(conn_params) 
            conn=super(DatabaseWrapper,self).get_new_connection(conn_params)
            logger.info("Successfully refreshed secret and established new database connection.")
            return conn

