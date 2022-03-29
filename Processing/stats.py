from sqlalchemy import Column, Integer, String, DateTime
from base import Base


class Stats(Base):
    """ Processing Statistics """

    __tablename__ = "stats"

    id = Column(Integer, primary_key=True)
    num_membercheckin_readings = Column(Integer, nullable=False)
    max_member_age_reading = Column(String(250), nullable=True)
    max_machine_name_reading = Column(String(250), nullable=True)
    num_gymequipmentuse_readings = Column(Integer, nullable=False)
    last_updated = Column(DateTime, nullable=False)


    def __init__(self, num_membercheckin_readings, max_member_age_reading, max_machine_name_reading, num_gymequipmentuse_readings, last_updated):
        """ Initializes a processing statistics object """
        self.num_membercheckin_readings = num_membercheckin_readings
        self.max_member_age_reading = max_member_age_reading
        self.max_machine_name_reading = max_machine_name_reading
        self.num_gymequipmentuse_readings = num_gymequipmentuse_readings
        self.last_updated = last_updated


    def to_dict(self):
        """ Dictionary Representation of a statistics """
        dict = {}
        dict['num_membercheckin_readings'] = self.num_membercheckin_readings
        dict['max_member_age_reading'] = self.max_member_age_reading
        dict['max_machine_name_reading'] = self.max_machine_name_reading
        dict['num_gymequipmentuse_readings'] = self.num_gymequipmentuse_readings
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%SZ")

        return dict