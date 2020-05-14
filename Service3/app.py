import connexion
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import yaml
import logging.config
import json
import requests
from flask_cors import CORS, cross_origin

try:
    with open('config/acit3855_service3_log_config.yml', 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)
except OSError as e:
    print("Log config file not found. Using default log config file.")
    with open('log_conf.yml', 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

try:
    with open('config/acit3855_service3_config.yml', 'r') as f:
        app_config = yaml.safe_load(f.read())
except OSError as e:
    logger.info("Config file not found. Using default config file.")
    with open('app_conf.yml', 'r') as f:
        app_config = yaml.safe_load(f.read())


def populate_stats():
    """ Periodically update stats """
    logger.info("Start Periodic Processing")

    stats = {
        "num_goals_scored": 0,
        "num_cards_received": 0,
        "updated_timestamp": "2000-01-01 00:00:01.001000"
    }

    with open(app_config['datastore']['filename'], 'r') as f:
        stats = json.loads(f.read())

    start_date = stats["updated_timestamp"]
    end_date = datetime.datetime.now()

    params = {
        "start_date": start_date,
        "end_date": end_date
    }

    r1 = requests.get('{}/stats/goals'.format(app_config['eventstore']['url']), params=params)

    if r1.status_code != 200:
        logger.error("Service error while getting updated stats for goals scored")
    else:
        logger.info("Number of goals scored events received: {}".format(len(r1.json())))

    r2 = requests.get('{}/stats/cards'.format(app_config['eventstore']['url']), params=params)

    if r2.status_code != 200:
        logger.error("Service error while getting updated stats for cards received")
    else:
        logger.info("Number of cards received events received: {}".format(len(r2.json())))

    new_stats = {
        "num_goals_scored": len(r1.json()) + stats["num_goals_scored"],
        "num_cards_received": len(r2.json()) + stats["num_cards_received"],
        "updated_timestamp": end_date.strftime("%Y-%m-%d %H:%M:%S.%f")
    }

    with open(app_config['datastore']['filename'], 'w') as f:
        json.dump(new_stats, f)

    logger.debug("new stats: {}".format(new_stats))

    logger.info("End Periodic Processing")


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()


def get_events_stats():
    logger.info("End Periodic Processing")

    stats = None
    with open(app_config['datastore']['filename'], 'r') as f:
        stats = json.loads(f.read())

    if stats is None:
        logger.error("Could not find stats file")

    logger.debug("new stats: {}".format(stats))
    logger.info("End Periodic Processing")

    return stats, 200


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml")

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)