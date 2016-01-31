from deckManagement import *
from deckManagementPrompts import *

def NewDeck():
	conn, curs = openConn()
	deckName, hero = getDeckInfo()
	cardList = getCardList()
	addCardsAndDeck(deckName, 0, hero, cardList, conn, curs)
	conn.close()