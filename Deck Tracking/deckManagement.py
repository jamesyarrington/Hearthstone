import sqlite3

defaultDB = 'hearthstone.db'
errorLog = 'errors.txt'
sampleCards = [('Magma Rager', 2),
				('Goldshire Footman', 2),
				('Sylvannas Windrunner', 1),
				('Execute', 2),
				('Fiery War Axe', 2)]

# Open a connection.
def openConn(dbName = defaultDB):
	conn = sqlite3.connect(dbName)
	curs = conn.cursor()
	return conn, curs

# If not given a connection and cursor, create new ones.
def checkConn(conn, curs, dbName = defaultDB):
	if conn:
		if not curs:
			curs = conn.cursor()
		return conn, curs, False
	else:
		curs, conn = openConn(dbName)
		return curs, conn, True

# Excecute a query, and record exception and sql query into log file.
def executeQuery(curs,query,logFile = errorLog):
	try:
		curs.execute(query)
		return
	except Exception as e:
		log = '''
			The error was:
				%s
			The Query was:
				%s''' % (str(e), query)
		logFile = open(logFile, 'w')
		logFile.write(log)
		logFile.close()
		raise e

# Add a deck to the tdecks table.  Return the deck_id.
def addDeck(deckName, revision, hero, conn = None, curs = None):
	conn, curs, new = checkConn(conn, curs)
	table = 'tdecks'

	insertQuery = '''INSERT INTO %s(
			deckname,
			revision,
			hero,
			created
			)
		VALUES(
			"%s",
			"%s",
			"%s",
			datetime('now')
			)
		''' % (table, deckName, revision, hero)

	executeQuery(curs,insertQuery)
	conn.commit()

	selectQuery = '''SELECT deck_id
		FROM %s
		WHERE(
			deckname = "%s" AND
			revision = "%s" AND
			hero = "%s"
			)
		''' % (table, deckName, revision, hero)

	executeQuery(curs,selectQuery)
	deck_id = curs.fetchone()[0]
	if new: conn.close()
	return deck_id

# Adds cards to tcards table.  cardList is a list of (cardName, quantity) tuples.
def addCards(deck_id, cardList, conn = None, curs = None):
	conn, curs, new = checkConn(conn, curs)
	table = 'tcards'

	for card in cardList:

		insertQuery = '''INSERT INTO %s(
				deck_id,
				cardname,
				quantity
				)
			VALUES(
				"%s",
				"%s",
				"%s"
				)
		''' % (table, deck_id, card[0], card[1])

		executeQuery(curs, insertQuery)
	conn.commit()
	if new: conn.close()

# Combine deck and card adding procedure.  Cards are added using the just added deck's ID.
def addCardsAndDeck(deckName, revision, hero, cardList, conn = None, curs = None):
	conn, curs, new = checkConn(conn, curs)
	deck_id = addDeck(deckName, revision, hero, conn, curs)
	addCards(deck_id, cardList, conn, curs)
	if new: conn.close()