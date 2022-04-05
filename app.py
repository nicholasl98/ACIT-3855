
import connexion
import mysql.connector
import pymysql
import yaml
import datetime
import logging
import logging.config
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from member_checkin import MemberCheckin
from gym_equipment import GymEquipment
from sqlalchemy import and_
from time import sleep



with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
    user = app_config["datastore"]["user"]
    password = app_config["datastore"]["password"]
    hostname = app_config["datastore"]["hostname"]
    port = app_config["datastore"]["port"]
    db = app_config["datastore"]["db"]


with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config) 


logger = logging.getLogger('basicLogger')


DB_ENGINE = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(user, password, hostname, port, db))

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


logger.info("Connecting to DB. Hostname:{}, Port:{}".format(hostname, port))

def report_member_checkin(body):
    """ Reports member that checked in and data """

    session = DB_SESSION()

    mc = MemberCheckin(body['member_id'],
                       body['member_age'],
                       body['member_name'],
                       body['member_time_entered'],
                       body['trace_id'])
                       

    session.add(mc)

    session.commit()
    session.close()

    received_event = "Stored event {} request with a trace id of {}".format("Report Member Check in", body['trace_id'])
    logger.debug(received_event)


def report_gym_equipment(body):
    """ Reports gym equipment in use and details """

    session = DB_SESSION()

    ge = GymEquipment(body['machine_id'],
                        body['machine_name'],
                        body['machine_time_used'],
                        body['trace_id'])

    session.add(ge)

    session.commit()
    session.close()

    received_event = "Stored event {} request with a trace id of {}".format("Report Gym Equipment", body['trace_id'])
    logger.debug(received_event)


def get_member_checkin(start_timestamp, end_timestamp):
    """ Gets new member check ins after the timestamp """

    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")

    readings = session.query(MemberCheckin).filter(
        and_(MemberCheckin.date_created >= start_timestamp_datetime,
        MemberCheckin.date_created < end_timestamp_datetime) )


    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for member check in readings after %s and before %s returns %d results" %
                (start_timestamp, end_timestamp, len(results_list)))

    return results_list, 200


def get_gym_equipment(start_timestamp, end_timestamp):
    """ Gets new gym equipment readings after the timestamp """

    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    
    readings = session.query(GymEquipment).filter(
        and_(GymEquipment.date_created >= start_timestamp_datetime,
        GymEquipment.date_created < end_timestamp_datetime) )

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for gym equipment use readings after %s and before %s returns %d results" %
                (start_timestamp, end_timestamp, len(results_list)))

    return results_list, 200

def process_messages():
    retry_count = 0
    """ Process event messages """
    hostname1 = "%s:%d" % (app_config["events"]["hostname"],   
                          app_config["events"]["port"]) 

    while retry_count < app_config["kafka_connect"]["retry_count"]:
        try:
            logger.info('trying to connect, attempt: %d' % (retry_count))
            print(hostname1)
            client = KafkaClient(hosts=hostname1)
        except:
            logger.info('attempt %d failed, retry in 5 seoncds' % (retry_count))
            retry_count += 1
            sleep(app_config["kafka_connect"]["sleep_time"])
        else:
            break
    logger.info('connected to kafka')

    topic = client.topics[str.encode(app_config["events"]["topic"])] 

    # Create a consumer on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)

    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)

        payload = msg["payload"]

        if msg["type"] == "membercheckin":  # Change this to your event type
        # Store the event1 (i.e., the payload) to the DB
            logger.info("Storing membercheckin event")
            report_member_checkin(payload)
        elif msg["type"] == "gymequipmentinuse":  # Change this to your event type
        # Store the event2 (i.e., the payload) to the DB
            logger.info("Storing gymequipmentinuse event")
            report_gym_equipment(payload)

        # Commit the new message as being read
        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
