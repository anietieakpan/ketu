# app/database/timeseries_db.py

from flask import current_app
from .base import DatabaseInterface
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime

class TimeSeriesDB(DatabaseInterface):
    def __init__(self, url=None, token=None, org=None, bucket=None):
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.client = None
        self.write_api = None
        
        # self.url = current_app.config['INFLUXDB_URL']
        # self.token = current_app.config['INFLUXDB_TOKEN']
        # self.org = current_app.config['INFLUXDB_ORG']
        # self.bucket = current_app.config['INFLUXDB_BUCKET']

    def connect(self):
        if not all([self.url, self.token, self.org, self.bucket]):
            self.url = current_app.config['INFLUXDB_URL']
            self.token = current_app.config['INFLUXDB_TOKEN']
            self.org = current_app.config['INFLUXDB_ORG']
            self.bucket = current_app.config['INFLUXDB_BUCKET']
            
        self.client = InfluxDBClient(
            url=self.url,
            token=self.token,
            org=self.org
            )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def disconnect(self):
        if self.client:
            self.client.close()

    def insert_detection(self, detection_data):
        try:
            point = Point("license_plate_detection") \
                .tag("plate", detection_data['text']) \
                .field("confidence", detection_data['confidence']) \
                .field("timestamp_local", detection_data['timestamp_local']) \
                .time(detection_data['timestamp_utc'])
            self.write_api.write(bucket=self.bucket, record=point)
            print(f"Data inserted into InfluxDB: {detection_data}")
        except Exception as e:
            print(f"Error inserting data into InfluxDB: {str(e)}")    

    def get_detections(self, start_time, end_time):
        query = f'''
        from(bucket:"{self.bucket}")
        |> range(start: {start_time.isoformat()}, stop: {end_time.isoformat()})
        |> filter(fn: (r) => r._measurement == "license_plate_detection")
        '''
        result = self.client.query_api().query(query, org=self.org)
        
        detections = []
        for table in result:
            for record in table.records:
                detections.append({
                    'plate': record.values.get('plate'),
                    'confidence': record.values.get('confidence'),
                    'timestamp_utc': record.get_time(),
                    'timestamp_local': record.values.get('timestamp_local')
                    # 'timestamp': record.values.get('_time')
                })
        return detections
    
    def update_detection(self, detection_id, update_data):
        # InfluxDB doesn't support updates in the same way as relational databases
        # For time-series data, we typically insert a new point instead of updating
        print("Warning: update_detection not implemented for TimeSeriesDB")
        pass

    def delete_detection(self, detection_id):
        # InfluxDB doesn't support deletes in the same way as relational databases
        # For time-series data, we typically use retention policies instead of deleting
        print("Warning: delete_detection not implemented for TimeSeriesDB")
        pass