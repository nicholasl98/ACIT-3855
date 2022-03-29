from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class GymEquipment(Base):
    """ Gym Equipment in use"""

    __tablename__ = "gym_equipment"
    id = Column(Integer, primary_key=True)
    machine_id = Column(String(250), nullable=False)
    machine_name = Column(String(250), nullable=False)
    machine_time_used = Column(String(100), nullable=False)
    trace_id = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)


    def __init__(self, machine_id, machine_name, machine_time_used, trace_id):
        """ Initializes gym equipment usage """
        self.machine_id = machine_id
        self.machine_name = machine_name
        self.machine_time_used = machine_time_used
        self.trace_id = trace_id
        self.date_created = datetime.datetime.now()

    def to_dict(self):
        """ Dictionary Representation of a gym equipment in use """
        dict = {}
        dict['id'] = self.id
        dict['machine_id'] = self.machine_id
        dict['machine_name'] = self.machine_name
        dict['machine_time_used'] = self.machine_time_used
        dict['trace_id'] = self.trace_id
        dict['date_created'] = self.date_created

        return dict