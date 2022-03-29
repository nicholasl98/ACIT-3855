from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class MemberCheckin(Base):
    """ Member Check in """

    __tablename__ = "member_checkin"
    id = Column(Integer, primary_key=True)
    member_id= Column(String(250), nullable=False)
    member_age = Column(String(250), nullable=False)
    member_name = Column(String(250), nullable=False)
    member_time_entered = Column(String(100), nullable=False)
    trace_id = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, member_id, member_age, member_name, member_time_entered, trace_id):
        """ Initializes a member that checked into the facility """
        self.member_id = member_id
        self.member_age = member_age
        self.member_name = member_name
        self.member_time_entered = member_time_entered
        self.trace_id = trace_id
        self.date_created = datetime.datetime.now()

    def to_dict(self):
        """ Dictionary Representation of a members entering the facility """
        dict = {}
        dict['id'] = self.id
        dict['member_id'] = self.member_id
        dict['member_age'] = self.member_age
        dict['member_name'] = self.member_name
        dict['member_time_entered'] = self.member_time_entered
        dict['trace_id'] = self.trace_id
        dict['date_created'] = self.date_created

        return dict
