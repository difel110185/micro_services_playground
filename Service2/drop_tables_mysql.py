import mysql.connector

conn = mysql.connector.connect(
   user='homestead', password='secret', host='localhost', port='33060', database='homestead'
)

c = conn.cursor()
c.execute('''
          DROP TABLE goals_scored
          ''')

c.execute('''
          DROP TABLE cards_received
          ''')

conn.commit()
conn.close()
