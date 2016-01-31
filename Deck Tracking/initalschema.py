import sqlite3


decks_schema = '''
	CREATE TABLE tdecks(
		deck_id		INTEGER		PRIMARY KEY,
		deckname	TEXT,
		revision	INTEGER,
		hero		TEXT,
		created		DATE
	)
	'''
	
cards_schema = '''
	CREATE TABLE tcards(
		card_id		INTEGER		PRIMARY KEY,
		deck_id		INTEGER,
		cardname	TEXT,
		quantity	INTEGER
	)
	'''

conn = sqlite3.connect('hearthstone.db')
curs = conn.cursor()

curs.execute(decks_schema)
curs.execute(cards_schema)

conn.commit()
conn.close()