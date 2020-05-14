import sqlite3

conn = sqlite3.connect('readings.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE goals_scored
          (id INTEGER PRIMARY KEY ASC, 
           player VARCHAR(100) NOT NULL,
           datetime VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

c.execute('''
          CREATE TABLE cards_received
          (id INTEGER PRIMARY KEY ASC, 
           player VARCHAR(100) NOT NULL,
           color VARCHAR(20) NOT NULL,
           datetime VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

conn.commit()
conn.close()
