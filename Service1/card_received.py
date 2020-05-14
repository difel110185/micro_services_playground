from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime as dt


class CardReceived(Base):
    """ Cards Received """

    __tablename__ = "cards_received"

    id = Column(Integer, primary_key=True)
    player = Column(String(250), nullable=False)
    color = Column(String(250), nullable=False)
    datetime = Column(String(250), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, player, color, datetime):
        """ Initializes a goal scored reading """
        self.player = player
        self.color = color
        self.datetime = datetime
        self.date_created = dt.datetime.now()

    def to_dict(self):
        """ Dictionary Representation of a card received reading """
        dict = {}
        dict['id'] = self.id
        dict['player'] = self.player
        dict['color'] = self.color
        dict['datetime'] = self.datetime

        return dict
