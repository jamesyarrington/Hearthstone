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

		stringIDs = [str(i) for i in self.all_ids]

		whereClause = listToString(stringIDs,
			beginsWith = 'WHERE(deck_id=',
			endsWith = ')',
			delim = '\nOR deck_id='
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

# Create a string from a list.
def listToString(inputList, beginsWith = '', endsWith = '', delim = ', '):

	for i, item in enumerate(inputList):

		if i == 0:
			outputString = beginsWith

		outputString += item

		if i == len(inputList) - 1:
			outputString += endsWith
		else:
			outputString += delim

	return outputString