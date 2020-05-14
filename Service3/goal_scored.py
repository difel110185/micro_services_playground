from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime as dt


class GoalScored(Base):
    """ Goal Scored """

    __tablename__ = "goals_scored"

    id = Column(Integer, primary_key=True)
    player = Column(String(250), nullable=False)
    datetime = Column(String(250), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, player, datetime):
        """ Initializes a goal scored reading """
        self.player = player
        self.datetime = datetime
        self.date_created = dt.datetime.now()

    def to_dict(self):
        """ Dictionary Representation of a goal scored reading """
        dict = {}
        dict['id'] = self.id
        dict['player'] = self.player
        dict['datetime'] = self.datetime

        return dict
