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

# Queries on the 'deck_id'(PK in tdecks) field in tcards to return a list of (cardname, quantity) tuples.
def getCardList(deck_id, conn = None, curs = None):
	conn, curs, new = checkConn(conn, curs)

	selectQuery = '''SELECT cardname, quantity
		FROM tcards
		WHERE(
			deck_id = %s
			)
		ORDER BY cardname''' % deck_id

	executeQuery(curs, selectQuery)
	cardList = curs.fetchall()
	if new: conn.close()
	return cardList

# Returns the most recently created deck_id, or all if specified.
def getDecks(deckName, hero, conn = None, curs = None, getAll = False,):
	conn, curs, new = checkConn(conn, curs)

	selectQuery = '''SELECT deck_id
		FROM tdecks
		WHERE(
			deckname = "%s" AND
			hero = "%s"
			)
		ORDER BY created DESC''' % (deckName, hero)

	executeQuery(curs, selectQuery)
	if getAll:
		deck_id = [deck[0] for deck in curs.fetchall()]
	else:
		deck_id = curs.fetchone()[0]
	if new: conn.close()
	return deck_id

# Checks if a deck has had the same list before.  Returns the deck_id of the repeat deck if so.  Deck_id cannot be 0.
def checkRepeatDeck(deckName, hero, newCardList, conn = None, curs = None):
	conn, curs, new = checkConn(conn, curs)
	previousDecks = getDecks(deckName, hero, conn, curs, getAll = True)
	for deck in previousDecks:
		if newCardList == getCardList(deck, conn, curs):
			if new: conn.close()
			return deck
	if new: conn.close()
	return False
	
# Checks if a card is in a cardList.  Assuming the card list is in alphabetical order.  Returns index of found card, or None if not found.
def cardInList(card,cardList):
	for i, item in enumerate(cardList):
		if card == item[0]:
			return i
		elif card < item[0]:
			return None
	return None

# Removes a card, a (cardName, quantity) tuple, from cardList.
def removeCard(card,cardList):
	location = cardInList(card[0],cardList)
	try:
		initQty = cardList[location][1]
	except TypeError:
		raise Exception('Tried to remove a card no longer in the deck!')
	except Exception as e:
		raise e
	newQty = initQty - card[1]
	if newQty > 0:
		newCard = (card[0], newQty)
		cardList[location] = newCard
	elif newQty == 0:
		cardList.pop(location)
	else:
		raise Exception('Tried to remove more of a card that exists in the deck!')

# Adds a card, a (cardName, quantity) tuple, to a cardList.
def addCard(card, cardList):
	location = cardInList(card[0],cardList)
	if location == None:
		cardList += [card]
		cardList.sort()
	else:
		newCard = (card[0], card[1] + cardList[location][1])
		cardList[location] = newCard

# Returns the highest revision of a deck, hero combination.
def getHighestRev(deckName, hero, conn = None, curs = None):
	conn, curs, new = checkConn(conn, curs)

	selectQuery = '''SELECT MAX(revision)
		FROM tdecks
		WHERE(
			deckname = "%s" AND
			hero = "%s"
			)
		ORDER BY created DESC''' % (deckName, hero)

	executeQuery(curs, selectQuery)
	revision = curs.fetchone()[0]
	if new: conn.close()
	return revision

# Update a deck's created datetime to the current time.
def updateCreatedTime(deck_id, conn = None, curs = None):
	conn, curs, new = checkConn(conn, curs)

	updateQuery = '''UPDATE tdecks
		SET
			created = datetime('now')
		WHERE(
			deck_id = %s
			)''' % deck_id

	executeQuery(curs, updateQuery)
	conn.commit()
	if new: conn.close()

# Creates a new revision of a deck (or reverts to an old one) based on the cards added and removed.
def updateDeck(deckName, hero, removedCards, addedCards, conn = None, curs = None):
	conn, curs, new = checkConn(conn, curs)
	latestDeck = getDecks(deckName, hero, conn, curs)
	cardList = getCardList(latestDeck, conn, curs)
	for card in removedCards:
		removeCard(card, cardList)
	for card in addedCards:
		addCard(card, cardList)
	sameDeck = checkRepeatDeck(deckName, hero, cardList, conn, curs)
	if sameDeck:
		updateCreatedTime(sameDeck, conn, curs)
	else:
		newRev = getHighestRev(deckName, hero, conn, curs) + 1
		addCardsAndDeck(deckName, newRev, hero, cardList, conn, curs)
	if new: conn.close()