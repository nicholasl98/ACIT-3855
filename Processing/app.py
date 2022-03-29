import connexion
import yaml
import logging
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler
import json
import requests
import datetime
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from stats import Stats


with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

# Create a basic logger
logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def populate_stats():
    """ Periodically update stats """
    logger.info("Start Periodic Processing")

    session = DB_SESSION()
    results = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    session.close()

    if not results:
        stats = {
            "num_membercheckin_readings": 0,
            "max_member_age_reading": 0,
            "max_machine_name_reading": 0,
            "num_gymequipmentuse_readings": 0,
            "last_updated": "2016-08-29T09:12:33Z"
        }
    else:
        stats = results.to_dict()

    previous_datetime = stats['last_updated']

    get_membercheckin = requests.get(app_config['eventstore1']['url'] + '?timestamp=' + previous_datetime)
    get_gymequipmentinuse = requests.get(app_config['eventstore2']['url'] + '?timestamp=' + previous_datetime)

    if get_membercheckin.status_code != 200:
        logger.error("Received a status code of {}".format(get_membercheckin.status_code))
    else:
        logger.info("Received {} events with a status code of {}".format(len(get_membercheckin.json()), get_membercheckin.status_code))

    if get_gymequipmentinuse.status_code != 200:
        logger.error("Received a status code of {}".format(get_gymequipmentinuse.status_code))
    else:
        logger.info("Received {} events with a status code of {}".format(len(get_gymequipmentinuse.json()), get_gymequipmentinuse.status_code))

     # Total number of membercheckin readings
    stats['num_membercheckin_readings'] = stats['num_membercheckin_readings'] + len(get_membercheckin.json())


    # Max member age reading
    max_member_age_reading = stats['max_member_age_reading']
    for event in get_membercheckin.json():
        logger.debug(event)
        if str(event['member_age']) > str(max_member_age_reading):
            max_member_age_reading = event['member_age']

    stats['max_member_age_reading'] = max_member_age_reading

   
    # Max gym equipment name in use reading
    max_machine_name_reading = stats['max_machine_name_reading']
    for event in get_gymequipmentinuse.json():
        logger.debug(event)
        if str(event['machine_name']) > str(max_machine_name_reading):
            max_machine_name_reading = event['machine_name']
            
    stats['max_machine_name_reading'] = max_machine_name_reading

    # Total number of gym equipment in use readings
    stats['num_gymequipmentuse_readings'] = stats['num_gymequipmentuse_readings'] + len(get_gymequipmentinuse.json())

    # Write updated stats to the database
    session = DB_SESSION()

    stats_new = Stats(stats["num_membercheckin_readings"],
                  stats["max_member_age_reading"],
                  stats["max_machine_name_reading"],
                  stats["num_gymequipmentuse_readings"],
                  datetime.datetime.now())

    session.add(stats_new)

    session.commit()
    session.close()

    logger.debug("Updated stats values: {}".format(stats))

    logger.info("End Periodic Processing")


def get_stats():
    """ Receives membercheckin and gymequipmentinuse readings processed statistics """
    logger.info("Request has started")

    session = DB_SESSION()
    results = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    session.close()

    if not results:
        stats = {
            "num_membercheckin_readings": 0,
            "max_member_age_reading": 0,
            "max_machine_name_reading": 0,
            "num_gymequipmentuse_readings": 0,
            "last_updated": "2016-08-29T09:12:33Z"
        }
    else:
        stats = results.to_dict()

    logger.debug(stats)

    logger.info("Request has completed")

    return stats, 200


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    # run our standalone gevent server
    init_scheduler()
    app.run(port=8100, use_reloader=False)
