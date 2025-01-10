from .timeseries_db import TimeSeriesDB
from .replica_db import ReplicaDB
from flask import current_app
import logging
# from config import Config


class DatabaseFactory:
    # @staticmethod
    # def get_database(db_type):
    #     logging.info("Attempting to get all databases")
    #     try:
    #         databases = {
    #             'timeseries': DatabaseFactory.get_database('timeseries'),
    #             'replica': DatabaseFactory.get_database('replica')
    #         }
    #         logging.info(f"Successfully created database instances: {list(databases.keys())}")
    #         return databases
    #     except Exception as e:
    #         logging.error(f"Error getting all databases: {str(e)}", exc_info=True)
    #         return None
    #     if db_type == 'timeseries':
    #         return TimeSeriesDB(
    #            url=current_app.config['INFLUXDB_URL'],
    #            token=current_app.config['INFLUXDB_TOKEN'],
    #            org=current_app.config['INFLUXDB_ORG'],
    #            bucket=current_app.config['INFLUXDB_BUCKET']
            
    #         )
        
    #     elif db_type == 'replica':
    #         return ReplicaDB()
    #     else:
    #         raise ValueError(f"Unsupported database type: {db_type}")

    @staticmethod
    def get_database(db_type):
        logging.info(f"Attempting to get database of type: {db_type}")
        try:
            if db_type == 'timeseries':
                logging.info("Creating TimeSeriesDB instance")
                return TimeSeriesDB(
                    url=current_app.config['INFLUXDB_URL'],
                    token=current_app.config['INFLUXDB_TOKEN'],
                    org=current_app.config['INFLUXDB_ORG'],
                    bucket=current_app.config['INFLUXDB_BUCKET']
                )
            elif db_type == 'replica':
                logging.info("Creating ReplicaDB instance")
                return ReplicaDB(
                    connection_string=current_app.config['SQLALCHEMY_DATABASE_URI']
                    
                )
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
        except Exception as e:
            logging.error(f"Error creating database instance: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_all_databases():
        return {
            'timeseries': DatabaseFactory.get_database('timeseries'),
            'replica': DatabaseFactory.get_database('replica')
        }

