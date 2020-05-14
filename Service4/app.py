import connexion
from connexion import NoContent
from pykafka import KafkaClient
from flask_cors import CORS, cross_origin
import json
import yaml
import logging.config

try:
    with open('config/acit3855_service4_log_config.yml', 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)
except OSError as e:
    print("Log config file not found. Using default log config file.")
    with open('log_conf.yml', 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

try:
    with open('config/acit3855_service4_config.yml', 'r') as f:
        app_config = yaml.safe_load(f.read())
except OSError as e:
    logger.info("Config file not found. Using default config file.")
    with open('app_conf.yml', 'r') as f:
        app_config = yaml.safe_load(f.read())


def get_nth_goal_scored(position):
    try:
        client = KafkaClient(hosts="{}:{}".format(app_config["kafka"]["domain"], app_config["kafka"]["port"]))
        topic = client.topics[app_config["kafka"]["topic"]]

        consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
        offset = 0
        for message in consumer:
            if message is not None and json.loads(message.value)['type'] == 'goals_scored':
                if offset == position:
                    logger.info("Nth goal scored retrieved successfully: Position {}".format(position))
                    return json.loads(message.value)['payload'], 200

                offset += 1
    except:
        logger.error("Service error while getting the nth goal scored")

    return NoContent, 404


def get_number_of_cards_reported(start_date, end_date):
    count = 0

    try:
        client = KafkaClient(hosts="{}:{}".format(app_config["kafka"]["domain"], app_config["kafka"]["port"]))
        topic = client.topics[app_config["kafka"]["topic"]]

        consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=10)

        for message in consumer:
            if message is not None and json.loads(message.value)['type'] == 'cards_received' and start_date <= json.loads(message.value)['datetime'] <= end_date:
                count += 1

        logger.info("Number of cards received retrieved from {} to {} successfully".format(start_date, end_date))
    except:
        logger.error("Service error while getting the number of cards received")

    return count, 200


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml")

if __name__ == "__main__":
    app.run(port=8110)