from deckManagement import *
from deckManagementPrompts import *

def newDeck():
	conn, curs = openConn()
	deckName, hero = promptDeckInfo()
	cardList = promptCardList()
	addCardsAndDeck(deckName, 0, hero, cardList, conn, curs)
	conn.close()

def editDeck():
	conn, curs = openConn()
	deckName, hero = promptDeckInfo()
	oldDeck = getDecks(deckName, hero, conn, curs)
	oldList = getCardList(oldDeck, conn, curs)
	removedCards, removedTotal = promptCardRemoval(oldList)
	print('You will be removing:')
	displayCardList(removedCards)
	print('Please enter the %s cards you would like to add.' % removedTotal)
	addedCards = promptCardList(removedTotal)
	updateDeck(deckName, hero, removedCards, addedCards, conn, curs)
	conn.close()