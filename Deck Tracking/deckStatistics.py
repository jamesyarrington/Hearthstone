from deckManagement import *


class Deck:

	def __init__(self, deck_id = -1, deckName = '', hero = ''):
		if deck_id > -1:
			self.deck_id = deck_id
			(self.deckName, self.hero) = getDeckInfo(deck_id)
		elif deckName:
			self.deckName = deckName
			self.hero = hero
			getDecks(deckName, hero)
		self.rev_dict = getAllRevs(self.deckName, self.hero)
		self.all_ids = list(self.rev_dict.keys())

	# return a (wins, losses) tuple based on the given conditions.
	def getPastResults(self, conditions = {}, conn = None, curs = None):

		conn, curs, new = checkConn(conn, curs)
		# First build the SELECT clause.
		selectClause = '''SELECT DISTINCT win, game_id
			FROM tgames NATURAL JOIN tplays
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

		cardConditionList = []

		cardConditionList += getCardActionStatement(conditions, 'PLAY')
		cardConditionList += getCardActionStatement(conditions, 'DRAW')
		cardConditionList += getCardActionStatement(conditions, 'DISCARD - DECK')
		cardConditionList += getCardActionStatement(conditions, 'DISCARD - HAND')
		cardConditionList += getCardActionStatement(conditions, 'PULL - DECK')
		cardConditionList += getCardActionStatement(conditions, 'PULL - HAND')

		cardConditionClause = listToString(cardConditionList,
			beginsWith = '(',
			endsWith = ')\n',
			delim = ')\nOR ('
			)

		if cardConditionClause:
			conditionList += [cardConditionClause]

		conditionList += getGameInfoStatement(conditions, 'opp_hero')
		conditionList += getGameInfoStatement(conditions, 'opp_deck')
		conditionList += getGameInfoStatement(conditions, 'game_mode')
		conditionList += getGameInfoStatement(conditions, 'turn')

		whereClause = listToString(conditionList,
			beginsWith = '\nWHERE(\n(',
			endsWith = ')\n)',
			delim = ')\nAND ('
			)

		# Then execute the query.

		selectQuery = selectClause + whereClause

		executeQuery(curs, selectQuery)
		results = [i[0] for i in curs.fetchall()]

		# Then count the wins (1) and losses (0).

		wins = results.count(1)
		losses = results.count(0)

		if new: conn.close()

		return (wins, losses)

	# returns a (wins, losses) tuple for a specific card in the deck.
	# A win only counts if the card was played (or pulled).
	# A loss counts if the card was drawn (or pulled from deck).
	def getCardRecord(self, cardName, conditions = {}):
		winConditions = copyDict(conditions)
		lossConditions = copyDict(conditions)

		winConditions['PLAY'] = cardName
		winConditions['PULL - HAND'] = cardName
		winConditions['PULL - DECK'] = cardName

		lossConditions['DRAW'] = cardName
		lossConditions['PULL - DECK'] = cardName

		wins = self.getPastResults(winConditions)[0]
		losses = self.getPastResults(lossConditions)[1]

		return (wins, losses)

	# Returns a (wins, losses) tuple for when the card was drawn on turn 0 or 1.
	def getMulliganRecord(self, cardName, conditions = {}):
		# This is sloppy.  I want to come back to this!
		conditions['DRAW'] = cardName
		conditions['turn'] = 0

		(wins, losses) = self.getPastResults(conditions)

		conditions['turn'] = 1

		(wins_t1, losses_t1) = self.getPastResults(conditions)

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
			AND action = '%s'
			''' % (playedCard, action)]

# Return a single element list in the form ["opp_hero = 'Hunter'"]
def getGameInfoStatement(conditions, field):
	try: data = conditions[field]
	except: return []
	else: return ["%s = '%s'" % (field, data)]