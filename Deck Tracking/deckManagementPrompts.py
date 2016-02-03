from genericPrompts import *

# Prompts the user for a deck name and hero.
def promptDeckInfo():
	name = input("What is the deck's name? ")
	hero = input("What is the deck's hero? ")
	return name, hero

# Prompts the user for a card name, and either 1 or 2 of that card.
def promptCardInfo():
	name = input("What is the card's name? ")
	quantity = getIntOrFalse('How many %ss would you like? ' % name, 1, 2)
	return name, quantity

# Creates a list of (cardName, quantity) tuples.
def promptCardList(total = 30):
	cardList = []
	while total > 0:
		print('Cards Left: %s' % total)
		name, quantity = promptCardInfo()
		total -= quantity
		if total < 0:
			print('You cannot have more than 30 cards!')
			total += quantity
			continue
		if quantity:
			cardList += [(name, quantity)]
	cardList.sort()
	return cardList

# Displays a numbered list of cards in the deck.
def displayCardList(cardList):
	for i, card in enumerate(cardList):
		if card[1] > 1:
			qtyString = ' (%s)' % card[1]
		else:
			qtyString = ''
		print('%s: %s%s' % (i + 1, card[0], qtyString))

# Prompts user to select a list of cards to remove.  Returns removed cardlist, and number of cards removed.
def promptCardRemoval(cardList):
	displayCardList(cardList)
	removedCards = []
	removedTotal = 0
	while True:
		selection = getIntOrFalse('Select a card to remove.  Leave blank to finish. ', 1, len(cardList)) - 1
		if selection > 0:
			selectedCard = cardList[selection]
			if selectedCard[1] == 1:
				quantity = 1
			else:
				quantity = getIntOrFalse('How many removed? ', 1, selectedCard[1])
			removedCards += [(selectedCard[0], quantity)]
			removedTotal += quantity
		else: return removedCards, removedTotal
