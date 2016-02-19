from deckManagement import *

# Create a new game entry in the database.  Return the database's game_id for that game.
def startGame(deck_id, opponentHero = 'UNKNOWN', opponentDeck = 'UNKNOWN', result = -1, conn = None, curs = None):
	conn, curs, new = checkConn(conn, curs)

	timestamp = strNow()

	insertQuery = '''INSERT INTO tgames(
			deck_id,
			opp_hero,
			opp_deck,
			win,
			time
			)
		VALUES(
			"%s",
			"%s",
			"%s",
			"%s",
			"%s"
			)
		''' % (deck_id, opponentHero, opponentDeck, result, timestamp)

	executeQuery(curs, insertQuery)
	conn.commit()

	selectQuery = '''SELECT game_id
		FROM tgames
		WHERE(
			time="%s"
			)
		''' % timestamp

	executeQuery(curs, selectQuery)
	game_id = curs.fetchone()[0]

	if new: conn.close()
	return game_id

# Update a previously created game.
def finishGame(game_id, opponentHero = 'UNKNOWN', opponentDeck = 'UNKNOWN', result = -1, conn = None, curs = None):
	conn, curs, new = checkConn(conn, curs)

	updateQuery = '''UPDATE tgames
		SET
			opp_hero = "%s",
			opp_deck = "%s",
			win = "%s"
		WHERE(
			game_id = "%s"
		)
		''' % (opponentHero, opponentDeck, result, game_id)

	executeQuery(curs, updateQuery)
	conn.commit()

	if new: conn.close()

# Record an action in the database.
def recordAction(game_id, cardName, action, turn, conn = None, curs = None):
	conn, curs, new = checkConn(conn, curs)

	insertQuery = '''INSERT INTO tplays(
			game_id,
			cardName,
			action,
			turn
		)
		VALUES(
			"%s",
			"%s",
			"%s",
			"%s"
		)
		''' % (game_id, cardName, action, turn)

	executeQuery(curs, insertQuery)
	conn.commit()

	if new: conn.close()

# Return the play_id of the earliest drawn (but unplayed) card.
def getDrawnCard(game_id, cardName, conn = None, curs = None):
	conn, curs, new = checkConn(conn, curs)

	selectQuery = '''SELECT play_id
		FROM tplays
		WHERE(
			game_id = "%s" AND
			cardName = "%s" AND
			turnplayed = 0
			)
		ORDER BY turndrawn ASC
		''' % (game_id, cardName)

	executeQuery(curs, selectQuery)
	play_id = curs.fetchone()[0]

	if new: conn.close()
	return play_id

# Record the play of an already drawn card.
def recordPlay(game_id, cardName, turn, conn = None, curs = None):
	conn, curs, new = checkConn(conn, curs)

	play_id = getDrawnCard(game_id, cardName, conn, curs)

	updateQuery = '''UPDATE tplays
		SET
			turnplayed = "%s"
		WHERE(
			play_id = "%s"
		)
		''' % (turn, play_id)

	executeQuery(curs, updateQuery)
	conn.commit()

	if new: conn.close()