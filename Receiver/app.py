import requests
import connexion
import yaml
import logging
import random
import logging.config
import datetime
import json
from pykafka import KafkaClient
from connexion import NoContent
from time import sleep

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
    membercheckin_url = app_config["eventstore1"]["url"]
    gymequipmentinuse_url = app_config["eventstore2"]["url"]
    kafka_server = app_config["events"]["hostname"]
    kafka_port = app_config["events"]["port"]
    tp = app_config["events"]["topic"]

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)


logger = logging.getLogger('basicLogger')

retry_count = 0
""" Process event messages """ 
hostname = "%s:%d" % (app_config["events"]["hostname"],   
                        app_config["events"]["port"]) 

while retry_count < app_config["kafka_connect"]["retry_count"]:
    try:
        logger.info('trying to connect, attempt: %d' % (retry_count))
        print(hostname)
        client = KafkaClient(hosts=hostname) 
        topic = client.topics[str.encode(app_config['events']['topic'])] 
        producer = topic.get_sync_producer() 
    except:
        logger.info('attempt %d failed, retry in 5 seoncds' % (retry_count))
        retry_count += 1
        sleep(app_config["kafka_connect"]["sleep_time"])
    else:
        break

logger.info('connected to kafka')

def report_member_checkin(body):
    headers = {"content-type": "application/json"}
    trace_id = str(random.randint(0, 9999999999))
    event_name = membercheckin_url.split("/")[-1]
    event_request = "Received event {} reading with a trace id of {}".format(event_name, trace_id)
    logger.info(event_request)
    body['trace_id'] = trace_id
    # response = requests.post(membercheckin_url, json=body, headers=headers)
    client = KafkaClient(hosts='{}:{}'.format(kafka_server, kafka_port))
    topic = client.topics[str.encode(tp)]
    producer = topic.get_sync_producer()
    msg = {"type": "membercheckin",
           "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    returned_event = "Returned event {} reading response id:{} reading with status {}".format(event_name, trace_id, 201)
    logger.info(returned_event)

    return NoContent, 201


def report_gym_equipment(body):

    headers = {"content-type": "application/json"}
    trace_id = str(random.randint(0, 9999999999))
    event_name = gymequipmentinuse_url.split("/")[-1]
    event_request = "Received event {} reading with a trace id of {}".format(event_name, trace_id)
    logger.info(event_request)
    body['trace_id'] = trace_id
    # response = requests.post(gymequipmentinuse_url, json=body, headers=headers)
    client = KafkaClient(hosts='{}:{}'.format(kafka_server, kafka_port))
    topic = client.topics[str.encode(tp)]
    producer = topic.get_sync_producer()
    msg = {"type": "gymequipmentinuse",
           "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    returned_event = "Returned event {} reading response id:{} reading with status {}".format(event_name, trace_id, 201)
    logger.info(returned_event)

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('openapi.yaml', strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)