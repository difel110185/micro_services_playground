import connexion

from connexion import NoContent
from pykafka import KafkaClient
from threading import Thread
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from goal_scored import GoalScored
from card_received import CardReceived
import yaml
import json
from flask_cors import CORS, cross_origin
import logging.config

try:
    with open('config/acit3855_service2_log_config.yml', 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)
except OSError as e:
    print("Log config file not found. Using default log config file.")
    with open('log_conf.yml', 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

try:
    with open('config/acit3855_service2_config.yml', 'r') as f:
        app_config = yaml.safe_load(f.read())
except OSError as e:
    logger.info("Config file not found. Using default config file.")
    with open('app_conf.yml', 'r') as f:
        app_config = yaml.safe_load(f.read())

DB_ENGINE = create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format(app_config["database"]["user"], app_config["database"]["password"], app_config["database"]["hostname"], app_config["database"]["port"], app_config["database"]["db"]))
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def get_goals_scored(start_date, end_date):
    if start_date is None or end_date is None:
        return NoContent, 400

    results_list = []

    try:
        session = DB_SESSION()

        results = session.query(GoalScored).filter(GoalScored.date_created.between(start_date, end_date))

        for result in results:
            results_list.append(result.to_dict())

        session.close()

        logger.info("Goals scored retrieved successfully from {} to {}".format(start_date, end_date))
    except:
        logger.error(e.args)
        return NoContent, 500

    return results_list, 200


def get_cards_received(start_date, end_date):
    if start_date is None or end_date is None:
        return NoContent, 400

    results_list = []

    try:
        session = DB_SESSION()

        results = session.query(CardReceived).filter(CardReceived.date_created.between(start_date, end_date))

        for result in results:
            results_list.append(result.to_dict())

        session.close()

        logger.info("Cards received retrieved successfully from {} to {}".format(start_date, end_date))
    except Exception as e:
        logger.error(e.args)
        return NoContent, 500

    return results_list, 200


def process_messages():
    client = KafkaClient(hosts="{}:{}".format(app_config["kafka"]["domain"], app_config["kafka"]["port"]))
    topic = client.topics[app_config["kafka"]["topic"]]

    while True:
        consumer = topic.get_simple_consumer(consumer_group=b"database_consumer", auto_commit_enable=True)
        message = consumer.consume(block=True)
        consumer.commit_offsets()
        if message is not None:
            msg_str = message.value.decode('utf-8')
            msg = json.loads(msg_str)

            print(msg)

            session = DB_SESSION()

            if msg['type'] == 'cards_received':
                session.add(CardReceived(msg['payload']['player'], msg['payload']['color'], msg['payload']['datetime']))
                logger.info("Card received added successfully".format(msg['payload']))
            elif msg['type'] == 'goals_scored':
                session.add(GoalScored(msg['payload']['player'], msg['payload']['datetime']))
                logger.info("Goal scored added successfully".format(msg['payload']))

            session.commit()
            session.close()



app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml")

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()

    app.run(port=8090)
