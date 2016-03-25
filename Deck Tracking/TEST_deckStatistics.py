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


class TestRecordRetrieve(TestCase):

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
			time.sleep(2) # Pause 2 seconds to get a new time stamp.
		self.assertEqual(self.deck.getPastResults(), (0, 5))

	def test_5and0(self):
		for i in range(0,5):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'DUMMY', 'DUMMY', 0)
			finishGame(game_id, result = 1)
			time.sleep(2) # Pause 2 seconds to get a new time stamp.
		self.assertEqual(self.deck.getPastResults(), (5, 0))

	def test_2and4(self):
		for i in range(0,2):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'DUMMY', 'DUMMY', 0)
			finishGame(game_id, result = 1)
			time.sleep(2) # Pause 2 seconds to get a new time stamp.
		for i in range(0,4):
			game_id = startGame(self.deck_id)
			recordAction(game_id, 'DUMMY', 'DUMMY', 0)
			finishGame(game_id, result = 0)
			time.sleep(2) # Pause 2 seconds to get a new time stamp.
		self.assertEqual(self.deck.getPastResults(), (2, 4))


suite = TestLoader().loadTestsFromTestCase(TestRecordRetrieve)
TextTestRunner(verbosity=2).run(suite)