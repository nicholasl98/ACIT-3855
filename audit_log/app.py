import connexion
import yaml
import logging
import logging.config
import json
from pykafka import KafkaClient


with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())


with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


def get_member_checkin(index):
    """ Get membercheckin in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    logger.info("Retrieving membercheckin at index %d" % index)
    counter = 0
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            payload = msg["payload"]
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
            if msg['type'] == 'membercheckin':
                if counter == index:
                    return payload, 200
                counter += 1
    except Exception as e:
        logger.error("No more messages found")
        logger.error(e)

    logger.error("Could not find membercheckin at index %d" % index)
    return {"message": "Not Found"}, 404


def get_gym_equipment(index):
    """ Get gym equipment usage in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    logger.info("Retrieving gym equipment usage at index %d" % index)
    counter = 0
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            payload = msg["payload"]
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
            if msg['type'] == 'gymequipmentinuse':
                if counter == index:
                    return payload, 200
                counter += 1
    except Exception as e:
        logger.error("No more messages found")
        logger

    logger.error("Could not find gym equipment in use at index %d" % index)
    return {"message": "Not Found"}, 404


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(port=8110)