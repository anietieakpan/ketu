from abc import ABC, abstractmethod

class DatabaseInterface(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def insert_detection(self, detection_data):
        pass

    @abstractmethod
    def get_detections(self, start_time, end_time):
        pass

    @abstractmethod
    def update_detection(self, detection_id, update_data):
        pass

    @abstractmethod
    def delete_detection(self, detection_id):
        pass