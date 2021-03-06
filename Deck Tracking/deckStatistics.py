from deckManagement import *


class Deck:

	def __init__(self, deck_id = -1, deckName = '', hero = ''):
		if deck_id > -1:
			self.deck_id = deck_id
			(self.deckName, self.hero) = getDeckInfo(deck_id)
		elif deckName:
			self.deckName = deckName
			self.hero = hero
			self.deck_id = getDecks(deckName, hero)
		self.rev_dict = getAllRevs(self.deckName, self.hero)
		self.all_ids = list(self.rev_dict.keys())

	# return a list of (game_id, result) tuples based on the given conditions.
	def getPastResults(self, conditions = {}, conn = None, curs = None):

		conn, curs, new = checkConn(conn, curs)
		# First build the SELECT clause.
		selectClause = '''SELECT game_id, win
			FROM tgames
			'''
		# Then build the WHERE clause.

		conditionList = []

		stringIDs = [str(i) for i in self.all_ids]
		conditionList += [
			listToString(stringIDs,
				beginsWith = 'deck_id=',
				endsWith = '',
				delim = '\nOR deck_id='
				)
			]

		conditionList += getGameInfoStatement(conditions, 'opp_hero')
		conditionList += getGameInfoStatement(conditions, 'opp_deck')
		conditionList += getGameInfoStatement(conditions, 'game_mode')

		whereClause = listToString(conditionList,
			beginsWith = '\nWHERE(\n(',
			endsWith = ')\n)',
			delim = ')\nAND ('
			)

		# Then execute the query.

		selectQuery = selectClause + whereClause
		executeQuery(curs, selectQuery)
		results = curs.fetchall()

		if new: conn.close()

		return results


	# returns a (wins, losses) tuple for a specific card in the deck, if 'CARD REC' is in the dict.
	# A win only counts if the card was played (or pulled).
	# A loss counts if the card was drawn (or pulled from deck).
	def getCardRecord(self, conditions = {}, number = 1):
		# Create the different conditions for when a card contributes to a win or loss.
		if 'CARD REC' in conditions:
			cardName = conditions['CARD REC']
			winConditions = copyDict(conditions)
			lossConditions = copyDict(conditions)

			winConditions['PLAY'] = cardName
			# winConditions['PULL - HAND'] = cardName
			# winConditions['PULL - DECK'] = cardName

			lossConditions['DRAW'] = cardName
			# lossConditions['PULL - DECK'] = cardName

		pastResults = self.getPastResults(conditions)
		adjustedResults = []

		for (game_id, result) in pastResults:

			cardConditions = conditions

			if 'CARD REC' in conditions:

				if result:
					cardConditions = winConditions
				else:
					cardConditions = lossConditions

			# Keep the record if it matches the card requirements.
			if checkCardConditions(game_id, cardConditions, number):
				adjustedResults += [(game_id, result)]

		pastResults = adjustedResults

		return getRecord(pastResults)

	# Function for sorting a list of(wins, losses) tuples.
	def winPercentage(self, record):
		return percentage(record[1])

	# Cycle through all cards currently in the deck.
	def getAllCardRecords(self, conditions = {}, threshold = 1):

		recordList = []
		for cardName in [card[0] for card in getCardList(self.deck_id)]:
			conditions['CARD REC'] = cardName
			record = self.getCardRecord(conditions)
			if record[0] + record[1] >= threshold:
				recordList += [(cardName, record, self.getCardRecord(conditions, 2), self.getMulliganRecord(cardName))]

		recordList.sort(key = self.winPercentage, reverse = True)

		return recordList



	# Returns a (wins, losses) tuple for when the card was drawn on turn 0 or 1.
	def getMulliganRecord(self, cardName, conditions = {}):
		# This is sloppy.  I want to come back to this!
		conditions['DRAW'] = cardName
		conditions['turn'] = 0

		(wins, losses) = self.getCardRecord(conditions)

		conditions['turn'] = 1

		(wins_t1, losses_t1) = self.getCardRecord(conditions)

		return (wins + wins_t1, losses + losses_t1)



# Create a copy of a dictionary.  copy does not share memory address.
def copyDict(dictionary):
	if dictionary:
		return { key : dictionary[key] for key in dictionary}
	else:
		return {}


# Create a string from a list.
def listToString(inputList, beginsWith = '', endsWith = '', delim = ', '):

	if inputList:

		for i, item in enumerate(inputList):

			if i == 0:
				outputString = beginsWith

			outputString += item

			if i == len(inputList) - 1:
				outputString += endsWith
			else:
				outputString += delim

		return outputString

	else: return ''

# Return a single element list in the form ["cardname = 'Magma Rager' AND action = 'PLAY']
def getCardActionStatement(conditions, action):
	try: playedCard = conditions[action]
	except: return []
	else:
		return ['''
			cardname = "%s"
			AND action = "%s"
			''' % (playedCard, action)]

# Return a single element list in the form ["opp_hero = 'Hunter'"]
def getGameInfoStatement(conditions, field):
	try: data = conditions[field]
	except: return []
	else: return ["%s = \"%s\"" % (field, data)]

# Check if a game meets the card-based conditions provided.
def checkCardConditions(game_id, conditions = {}, number = 1, conn = None, curs = None):

	conn, curs, new = checkConn(conn, curs)

	selectClause = '''SELECT game_id
		FROM tgames NATURAL JOIN tplays
		'''

	conditionList = ['game_id = "%s"' % game_id]
	conditionList += getGameInfoStatement(conditions, 'turn')

	conditionList += getCardActionStatement(conditions, 'PLAY')
	conditionList += getCardActionStatement(conditions, 'DRAW')
	conditionList += getCardActionStatement(conditions, 'DISCARD - DECK')
	conditionList += getCardActionStatement(conditions, 'DISCARD - HAND')
	conditionList += getCardActionStatement(conditions, 'PULL - DECK')
	conditionList += getCardActionStatement(conditions, 'PULL - HAND')


	whereClause = listToString(conditionList,
		beginsWith = '\nWHERE(\n(',
		endsWith = ')\n)',
		delim = ')\nAND ('
		)

	selectQuery = selectClause + whereClause

	executeQuery(curs, selectQuery)

	# Consume query results so that the test below determines if the card was played X times.
	for i in range(number - 1):
		curs.fetchone()

	# Return true if the game meets the criteria (query returns a result).	
	meetsConditions = curs.fetchone() is not None

	if new: conn.close()

	return meetsConditions

# Formats a list of (game_id, result) tuples into a (wins, losses) tuple.
def getRecord(results):
	results = [result[1] for result in results]
	# Count the wins (1) and losses (1) in the remaining results.
	return (results.count(1), results.count(0))

def percentage(record):
	total = record[0] + record[1]
	if total:
		return record[0]/total
	else:
		return 0

def recordString(record, thresh = 1):
	if record[0] + record[1] >= thresh:
		return "%2.0f - %2.0f (%3.0f%%)" % (record[0], record[1], 100*percentage(record))
	else:
		return "-- -- --".center(14)


# Return the results of the last 'number' games (game_id, win, opp_hero, opp_deck)
def getLastGames(number, mode = 'Standard Ranked', conn = None, curs = None):

	conn, curs, new = checkConn(conn, curs)

	selectQuery = '''SELECT game_id, win, opp_hero, opp_deck
		FROM tgames
		WHERE game_mode = "%s"
		ORDER BY `time` DESC
		LIMIT %s
		''' % (mode, number)

	executeQuery(curs, selectQuery)
	results = curs.fetchall()
	if new: conn.close()

	return results

def sortedLastGames(number, mode = 'Standard Ranked'):
	if not mode:
		mode = 'Standard Ranked'
	justOpp = [(game[2], game[3]) for game in getLastGames(number, mode)]
	gameSet = set(justOpp)
	gameList = [(justOpp.count(opp), opp[0], opp[1]) for opp in gameSet]
	gameList.sort(reverse = True)
	return gameList