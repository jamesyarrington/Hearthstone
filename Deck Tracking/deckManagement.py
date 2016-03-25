import sqlite3
import datetime
import db_globals


errorLog = 'errors.txt'
sampleCards = [('Magma Rager', 2),
				('Goldshire Footman', 2),
				('Sylvannas Windrunner', 1),
				('Execute', 2),
				('Fiery War Axe', 2)]

# Open a connection.
def openConn(dbName):
	conn = sqlite3.connect(dbName)
	curs = conn.cursor()
	return conn, curs

# If not given a connection and cursor, create new ones.
def checkConn(conn, curs):
	if conn:
		if not curs:
			curs = conn.cursor()
		return conn, curs, False
	else:
		curs, conn = openConn(db_globals.dbName)
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

# I think it is dumb that I have to make a function to clean up
# getting timestamp of current time.
def strNow(format = '%Y-%m-%d %H:%M:%S'):
	dummytime = datetime.datetime(1, 1, 1, 1, 1, 1)
	now = dummytime.now()
	return now.strftime(format)

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
			"%s"
			)
		''' % (table, deckName, revision, hero, strNow())

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
def getDecks(deckName, hero, conn = None, curs = None, getAll = False):
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

# Returns the deck, hero combination for the given deck_id.
def getDeckInfo(deck_id, conn = None, curs = None):
	conn, curs, new = checkConn(conn, curs)

	selectQuery = '''SELECT deckname, hero
		FROM tdecks
		WHERE(
			deck_id = "%s"
			)
		ORDER BY created DESC''' % deck_id

	executeQuery(curs, selectQuery)
	(deckName, hero) = curs.fetchone()
	if new: conn.close()
	return deckName, hero

# Update a deck's created datetime to the current time.
def updateCreatedTime(deck_id, conn = None, curs = None):
	conn, curs, new = checkConn(conn, curs)

	updateQuery = '''UPDATE tdecks
		SET
			created = "%s"
		WHERE(
			deck_id = %s
			)''' % (strNow(), deck_id)

	executeQuery(curs, updateQuery)
	conn.commit()
	if new: conn.close()

# Creates a new revision of a deck (or reverts to an old one) based on the cards added and removed.
def updateDeck(deckName, hero, removedCards, addedCards, conn = None, curs = None, deck_id = None):
	conn, curs, new = checkConn(conn, curs)
	if deck_id == None:
		latestDeck = getDecks(deckName, hero, conn, curs)
	else:
		latestDeck = deck_id
	cardList = getCardList(latestDeck, conn, curs)
	for card in removedCards:
		removeCard(card, cardList)
	for card in addedCards:
		addCard(card, cardList)
	storeNewCardList(deckName, hero, cardList, conn, curs)
	if new: conn.close()

# Creates a new revision of a deck (or reverts to an old one), based on new deck list
def storeNewCardList(deckName, hero, cardList, conn = None, curs = None):
	conn, curs, new = checkConn(conn, curs)
	sameDeck = checkRepeatDeck(deckName, hero, cardList, conn, curs)
	if sameDeck:
		updateCreatedTime(sameDeck, conn, curs)
	else:
		newRev = getHighestRev(deckName, hero, conn, curs) + 1
		addCardsAndDeck(deckName, newRev, hero, cardList, conn, curs)
	if new: conn.close()

# Converts the card list to a string.
def cardListAsString(cardList):
	cardListString = ''
	for i, card in enumerate(cardList):
		cardListString += '%s: %s\n' % (i + 1, singleCardString(card))
	return cardListString

# Converts a single, (cardName, quantity) tuple, into a string
def singleCardString(card):
	if card[1] > 1:
		qtyString = ' (%s)' % card[1]
	else:
		qtyString = ''
	return card[0] + qtyString


# Return a list of (deck_id, deckName, hero) tuples of the current revision of all decks.
def getDistinctDecks(conn = None, curs = None):
	conn, curs, new = checkConn(conn, curs)

	selectQuery = '''SELECT DISTINCT deckname, hero
		FROM tdecks'''

	executeQuery(curs, selectQuery)

	decks = []
	for result in curs:
		(deckName, hero) = result
		deck_id = getDecks(deckName, hero) # Not using curs from parent, as it is an iterator in this loop.
		decks += [(deck_id, deckName, hero)]

	if new: conn.close()
	return decks

# Returns a deck_id : revision dictionary for the given deckName, hero input.
def getAllRevs(deckName, hero, conn = None, curs = None):
	conn, curs, new = checkConn(conn, curs)

	deck_ids = getDecks(deckName, hero, conn, curs, getAll = True)

	idsAndRevs = {}

	for deck_id in deck_ids:
		idsAndRevs[deck_id] = getRev(deck_id, conn, curs)

	if new: conn.close()

	return idsAndRevs


# Returns the revision of the given deck.
def getRev(deck_id, conn = None, curs = None):
	conn, curs, new = checkConn(conn, curs)

	selectQuery = '''SELECT revision
		FROM tdecks
		WHERE(
			deck_id = %s
			)''' % deck_id

	executeQuery(curs, selectQuery)
	revision = curs.fetchone()

	if new: conn.close()

	return revision