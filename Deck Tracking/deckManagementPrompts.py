from genericPrompts import *

# Prompts the user for a deck name and hero.
def getDeckInfo():
	name = input("What is the deck's name? ")
	hero = input("What is the deck's hero? ")
	return name, hero

# Prompts the user for a card name, and either 1 or 2 of that card.
def getCardInfo():
	name = input("What is the card's name? ")
	quantity = getIntOrFalse('How many %ss would you like?' % name, 1, 2)
	return name, quantity

# Creates a list of (cardName, quantity) tuples.
def getCardList(total = 30):
	cardList = []
	while total > 0:
		print('Cards Left: %s' % total)
		name, quantity = getCardInfo()
		total -= quantity
		if total < 0:
			print('You cannot have more than 30 cards!')
			total += quantity
			continue
		if quantity:
			cardList += [(name, quantity)]
	cardList.sort()
	return cardList