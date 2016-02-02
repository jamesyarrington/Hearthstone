from deckManagement import *
from deckManagementPrompts import *

def NewDeck():
	conn, curs = openConn()
	deckName, hero = promptDeckInfo()
	cardList = promptCardList()
	addCardsAndDeck(deckName, 0, hero, cardList, conn, curs)
	conn.close()