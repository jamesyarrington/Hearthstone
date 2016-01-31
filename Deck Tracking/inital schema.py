import sqlite3


initial_schema = '''
	CREATE TABLE tdecks(
		deck_id		INTEGER	PRIMARY KEY
		deckname	TEXT
		revision	INTEGER
		hero		TEXT
		created		DATE
	)
	CREATE TABLE tcards(
		card_id		INTEGER PRIMARY KEY
		deck_id		INTEGER
		cardname	TEXT
		quantity	INTEGER
	)
	'''

conn = sqlite3.connect('hearthstone.db')
curs = conn.cursor()

curs.execute(inital_schema)

conn.commit()
conn.close()