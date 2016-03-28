from deckStatistics import *
from gameManagement import *
from initialschema import *
import db_globals

import os
import time
from unittest import TestCase, TestSuite, TestLoader, TextTestRunner



def initDB():
	setupDatabase(db_globals.dbName)

def deleteDB():
	os.remove('temp.db')

def dummyDeck():
	return addDeck(
		deckName = 'dummyNAME',
		revision = '1',
		hero = 'dummyHERO'
		)

def dummyList(deck_id):
	cardList = [
	('two_Of', 2)
	('one_Of', 1)
	]
	addCards(deck_id, cardList)


class Test_getPastResults(TestCase):

	def setUp(self):
		db_globals.dbName = 'temp.db'
		initDB()
		self.deck_id = dummyDeck()
		self.deck = Deck(deck_id = self.deck_id)

	def tearDown(self):
		deleteDB()

	def test_0and5(self):
		for i in range(0,5):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'DUMMY', 'DUMMY', 0)
			finishGame(game_id, result = 0)
			time.sleep(1) # Pause 1 second to get a new time stamp.
		self.assertEqual(self.deck.getPastResults(), (0, 5))

	def test_5and0(self):
		for i in range(0,5):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'DUMMY', 'DUMMY', 0)
			finishGame(game_id, result = 1)
			time.sleep(1) # Pause 1 second to get a new time stamp.
		self.assertEqual(self.deck.getPastResults(), (5, 0))

	def test_2and4(self):
		for i in range(0,2):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'DUMMY', 'DUMMY', 0)
			finishGame(game_id, result = 1)
			time.sleep(1) # Pause 1 second to get a new time stamp.
		for i in range(0,4):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'DUMMY', 'DUMMY', 0)
			finishGame(game_id, result = 0)
			time.sleep(1) # Pause 1 second to get a new time stamp.
		self.assertEqual(self.deck.getPastResults(), (2, 4))

	def test_2and0card(self):
		for i in range(0,2):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'DUMMY', 'PLAY', 0)
			finishGame(game_id, result = 1)
			time.sleep(1) # Pause 1 second to get a new time stamp.
		for i in range(0,4):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'OTHER DUMMY', 'PLAY', 0)
			finishGame(game_id, result = 0)
			time.sleep(1) # Pause 1 second to get a new time stamp.
		conditions = {'PLAY' : 'DUMMY'}
		self.assertEqual(self.deck.getPastResults(conditions), (2, 0))

	def test_3and1card(self):
		for i in range(0,3):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'DUMMY', 'PLAY', 0)
			finishGame(game_id, result = 1)
			time.sleep(1) # Pause 1 second to get a new time stamp.
		for i in range(0,1):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'DUMMY', 'PLAY', 0)
			finishGame(game_id, result = 0)
			time.sleep(1) # Pause 1 second to get a new time stamp.
		for i in range(0,1):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'OTHER DUMMY', 'PLAY', 0)
			finishGame(game_id, result = 0)
			time.sleep(1) # Pause 1 second to get a new time stamp.
		for i in range(0,1):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'OTHER DUMMY', 'PLAY', 0)
			finishGame(game_id, result = 1)
			time.sleep(1) # Pause 1 second to get a new time stamp.
		conditions = {'PLAY' : 'DUMMY'}
		self.assertEqual(self.deck.getPastResults(conditions), (3, 1))

	def test_facehunter2and0(self):
		for i in range(0,2):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'DUMMY', 'PLAY', 0)
			finishGame(game_id, result = 1, opponentHero = 'Hunter', opponentDeck = 'Face')
			time.sleep(1) # Pause 1 second to get a new time stamp.
		for i in range(0,1):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'DUMMY', 'PLAY', 0)
			finishGame(game_id, result = 0, opponentHero = 'Hunter', opponentDeck = 'Reno')
			time.sleep(1) # Pause 1 second to get a new time stamp.
		conditions = {
			'opp_hero' : 'Hunter',
			'opp_deck' : 'Face'
			}
		self.assertEqual(self.deck.getPastResults(conditions), (2, 0))

	def test_faceshaman3and1(self):
		for i in range(0,3):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'DUMMY', 'PLAY', 0)
			finishGame(game_id, result = 1, opponentHero = 'Shaman', opponentDeck = 'Face')
			time.sleep(1) # Pause 1 second to get a new time stamp.
		for i in range(0,1):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'DUMMY', 'PLAY', 0)
			finishGame(game_id, result = 0, opponentHero = 'Shaman', opponentDeck = 'Face')
			time.sleep(1) # Pause 1 second to get a new time stamp.
		for i in range(0,1):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'DUMMY', 'PLAY', 0)
			finishGame(game_id, result = 0, opponentHero = 'Hunter', opponentDeck = 'Face')
			time.sleep(1) # Pause 1 second to get a new time stamp.
		for i in range(0,1):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'DUMMY', 'PLAY', 0)
			finishGame(game_id, result = 1, opponentHero = 'Shaman', opponentDeck = 'BattleCry')
			time.sleep(1) # Pause 1 second to get a new time stamp.
		conditions = {
			'opp_hero' : 'Shaman',
			'opp_deck' : 'Face'
			}
		self.assertEqual(self.deck.getPastResults(conditions), (3, 1))

	def test_facehunter2and1withChow(self):
		for i in range(0,2):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'Zombie Chow', 'PLAY', 0)
			finishGame(game_id, result = 1, opponentHero = 'Hunter', opponentDeck = 'Face')
			time.sleep(1) # Pause 1 second to get a new time stamp.
		for i in range(0,1):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'Magma Rager', 'PLAY', 0)
			finishGame(game_id, result = 0, opponentHero = 'Hunter', opponentDeck = 'Face')
			time.sleep(1) # Pause 1 second to get a new time stamp.
		for i in range(0,1):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'Zombie Chow', 'PLAY', 0)
			finishGame(game_id, result = 0, opponentHero = 'Hunter', opponentDeck = 'Face')
			time.sleep(1) # Pause 1 second to get a new time stamp.
		for i in range(0,1):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'Zombie Chow', 'PLAY', 0)
			finishGame(game_id, result = 1, opponentHero = 'Shaman', opponentDeck = 'Reno')
			time.sleep(1) # Pause 1 second to get a new time stamp.
		for i in range(0,1):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'Zombie Chow', 'DRAW', 0)
			finishGame(game_id, result = 0, opponentHero = 'Hunter', opponentDeck = 'Face')
			time.sleep(1) # Pause 1 second to get a new time stamp.
		conditions = {
			'opp_hero' 	: 'Hunter',
			'opp_deck' 	: 'Face',
			'PLAY'		: 'Zombie Chow'
			}
		self.assertEqual(self.deck.getPastResults(conditions), (2, 1))

	def test_1and2record(self):
		for i in range(0,1):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'Zombie Chow', 'PLAY', 0)
			finishGame(game_id, result = 1)
			time.sleep(1) # Pause 1 second to get a new time stamp.
		for i in range(0,2):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'Zombie Chow', 'DRAW', 0)
			finishGame(game_id, result = 0)
			time.sleep(1) # Pause 1 second to get a new time stamp.
		for i in range(0,1):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'Leper Gnome', 'PLAY', 0)
			finishGame(game_id, result = 0)
			time.sleep(1) # Pause 1 second to get a new time stamp.
		for i in range(0,3):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'Zombie Chow', 'DRAW', 0)
			finishGame(game_id, result = 1)
			time.sleep(1) # Pause 1 second to get a new time stamp.
		conditions = {
			'CARD REC' 	: "Zombie Chow"
			}
		self.assertEqual(self.deck.getCardRecord(conditions), (1, 2))

	def test_cardWithApostrophe(self):
		for i in range(0,1):
			game_id = startGame(self.deck_id)
			recordAction(game_id, "Vol'jin", 'PLAY', 0)
			finishGame(game_id, result = 1)
			time.sleep(1) # Pause 1 second to get a new time stamp.
		for i in range(0,1):
			game_id = startGame(self.deck_id)
			recordAction(game_id, "N'Zoth", 'DRAW', 0)
			finishGame(game_id, result = 0)
			time.sleep(1) # Pause 1 second to get a new time stamp.
		conditions = {
			'CARD REC' 	: "Vol'jin"
			}
		self.assertEqual(self.deck.getCardRecord(conditions), (1, 0))

	def test_mulliganRecord(self):
		for i in range(0,3):
			game_id = startGame(self.deck_id)
			recordAction(game_id, "Zombie Chow", 'DRAW', i)
			finishGame(game_id, result = 1)
			time.sleep(1) # Pause 1 second to get a new time stamp.
		for i in range(0,1):
			game_id = startGame(self.deck_id)
			recordAction(game_id, "Loot Hoarder", 'DRAW', 0)
			finishGame(game_id, result = 0)
			time.sleep(1) # Pause 1 second to get a new time stamp.
		self.assertEqual(self.deck.getMulliganRecord("Zombie Chow"), (2, 0))

	def test_mulliganFaceHunter(self):
		for i in range(0,3):
			game_id = startGame(self.deck_id)
			recordAction(game_id, "Zombie Chow", 'DRAW', i)
			finishGame(game_id, result = 1, opponentHero = 'Hunter', opponentDeck = 'Face')
			time.sleep(1) # Pause 1 second to get a new time stamp.
		for i in range(0,1):
			game_id = startGame(self.deck_id)
			recordAction(game_id, "Loot Hoarder", 'DRAW', 0)
			finishGame(game_id, result = 0, opponentHero = 'Hunter', opponentDeck = 'Face')
			time.sleep(1) # Pause 1 second to get a new time stamp.
		for i in range(0,3):
			game_id = startGame(self.deck_id)
			recordAction(game_id, "Zombie Chow", 'DRAW', i)
			finishGame(game_id, result = 0, opponentHero = 'Shaman', opponentDeck = 'Face')
			time.sleep(1) # Pause 1 second to get a new time stamp.
		conditions = {
			'opp_hero' 	: 'Hunter',
			'opp_deck' 	: 'Face'
			}
		self.assertEqual(self.deck.getMulliganRecord("Zombie Chow", conditions), (2, 0))



suite = TestLoader().loadTestsFromTestCase(Test_getPastResults)
TextTestRunner(verbosity=2).run(suite)