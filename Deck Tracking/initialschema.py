import sqlite3

def setupDatabase(databaseName):
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

	games_schema = '''
		CREATE TABLE tgames(
			game_id		INTEGER		PRIMARY KEY,
			deck_id		INTEGER,
			opp_hero	TEXT,
			opp_deck	TEXT,
			game_mode	TEXT,
			win			INTEGER,
			time		DATE
		)
		'''

	plays_schema = '''
		CREATE TABLE tplays(
			play_id		INTEGER		PRIMARY KEY,
			game_id		INTEGER,
			cardname	TEXT,
			action		TEXT,
			turn		INTEGER
		)
		'''


	conn = sqlite3.connect(databaseName)
	curs = conn.cursor()
	curs.execute(decks_schema)
	curs.execute(cards_schema)
	curs.execute(games_schema)
	curs.execute(plays_schema)

	conn.commit()
	conn.close()