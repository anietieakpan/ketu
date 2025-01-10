from .base import DatabaseInterface
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class LicensePlateDetection(Base):
    __tablename__ = 'license_plate_detections'

    id = Column(Integer, primary_key=True)
    plate_text = Column(String, index=True)
    confidence = Column(Float)
    timestamp = Column(DateTime, index=True)

class ReplicaDB(DatabaseInterface):
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.engine = None
        self.Session = None

    def connect(self):
        self.engine = create_engine(self.connection_string)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def disconnect(self):
        if self.engine:
            self.engine.dispose()

    def insert_detection(self, detection_data):
        session = self.Session()
        try:
            new_detection = LicensePlateDetection(
                plate_text=detection_data['text'],
                confidence=detection_data['confidence'],
                timestamp=detection_data['timestamp'],
            )
            session.add(new_detection)
            session.commit()
        finally:
            session.close()

    def get_detections(self, start_time, end_time):
        session = self.Session()
        try:
            detections = session.query(LicensePlateDetection).filter(
                LicensePlateDetection.timestamp.between(start_time, end_time)
            ).all()
            return [self._detection_to_dict(d) for d in detections]
        finally:
            session.close()

    def update_detection(self, detection_id, update_data):
        session = self.Session()
        try:
            detection = session.query(LicensePlateDetection).get(detection_id)
            if detection:
                for key, value in update_data.items():
                    setattr(detection, key, value)
                session.commit()
                return True
            return False
        finally:
            session.close()

    def delete_detection(self, detection_id):
        session = self.Session()
        try:
            detection = session.query(LicensePlateDetection).get(detection_id)
            if detection:
                session.delete(detection)
                session.commit()
                return True
            return False
        finally:
            session.close()

    def _detection_to_dict(self, detection):
        return {
            'id': detection.id,
            'text': detection.plate_text,
            'confidence': detection.confidence,
            'timestamp': detection.timestamp,
        }

    def analyze_following_vehicles(self, subject_plate, time_window):
        session = self.Session()
        try:
            # This is a simplified example. In a real-world scenario, 
            # you'd need a more complex algorithm to determine following vehicles.
            subject_detections = session.query(LicensePlateDetection).filter(
                LicensePlateDetection.plate_text == subject_plate,
                LicensePlateDetection.timestamp >= datetime.now() - time_window
            ).order_by(LicensePlateDetection.timestamp).all()

            following_vehicles = []
            for i in range(len(subject_detections) - 1):
                potential_followers = session.query(LicensePlateDetection).filter(
                    LicensePlateDetection.plate_text != subject_plate,
                    LicensePlateDetection.timestamp.between(
                        subject_detections[i].timestamp,
                        subject_detections[i+1].timestamp
                    )
                ).all()

                for follower in potential_followers:
                    if follower.plate_text not in following_vehicles:
                        following_vehicles.append(follower.plate_text)

            return following_vehicles
        finally:
            session.close()