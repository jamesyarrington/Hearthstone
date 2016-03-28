from tkinter import *
from deckManagement import *
from gameManagement import *
from deckStatistics import *
from functools import partial

import db_globals
db_globals.dbName = 'hearthstone.db'


# Class for the inital window.  Has buttons to go to EDIT DECK or NEW DECK.
class MainWindow:

	def __init__(self, master):

		self.master = master

		frame = Frame(master)
		frame.pack()

		self.button0 = Button(frame, text = 'NEW DECK', bg = 'green', command = self.newDeck)
		self.button0.pack(side = LEFT)

		self.button1 = Button(frame, text = 'EDIT DECK', bg = 'red', command = self.editDeck)
		self.button1.pack(side = LEFT)

		self.button2 = Button(frame, text = 'PLAY GAME', bg = 'white', command = self.playGame)
		self.button2.pack(side = LEFT)

		self.button3 = Button(frame, text = 'DECK STATS', bg = 'white', command = self.deckStats)
		self.button3.pack(side = LEFT)

	# Prompt the user for deckName and hero, then open the DeckCreator.
	def newDeck(self):
		newWindow = Toplevel(self.master)
		di = DeckInfoWindow(newWindow, message = 'Enter the name and hero of a new deck!')
		 # Need to add check if exists later.

	# Present the user with a list of buttons to select a deck to edit.
	def editDeck(self):
		newWindow = Toplevel(self.master)
		di = DeckSelector(newWindow, DeckCreator)

	# Present the user with a list of buttons to select a deck to play.
	def playGame(self):
		newWindow = Toplevel(self.master)
		di = DeckSelector(newWindow, GameTracker)

	# Present the user with a list of buttons to select a deck to play.
	def deckStats(self):
		newWindow = Toplevel(self.master)
		di = DeckSelector(newWindow, DeckStats)

# Class for the window to edit a deck.  Enter a card name in the text box, then either "ADD 1" or "ADD 2".
# When done, hit "DONE" to add the deck into the database and close the window.
class DeckCreator:

	def __init__(self, master, deck_id, parent = False):

		self.listDisplay = StringVar()
		self.newCardList = getCardList(deck_id)
		self.deck_id = deck_id
		self.master = master
		self.parent = parent

		self.cardEntry = Entry(master)
		self.cardEntry.pack()
		self.cardEntry.place(x = 0, y = 20, height = 25, width = 150)

		self.addOne = Button(master, text = 'ADD 1', command = self.addOneCard)
		self.addOne.pack()
		self.addOne.place(x = 155, y = 0, height = 30, width = 75)

		self.addTwo = Button(master, text = 'ADD 2', command = self.addTwoCards)
		self.addTwo.pack()
		self.addTwo.place(x = 155, y = 30, height = 30, width = 75)

		self.done = Button(master, text = 'DONE', command = self.finish)
		self.done.pack()
		self.done.place(x = 235, y = 0, height = 60, width = 60)

		self.cardButtons = ButtonArray(master, self.newCardList, buttonLeftClick = self.deleteCard, pos = (5, 75))

	# Wrappers for inserting either 1 or two cards.
	def addOneCard(self): self.insertCard(1)
	def addTwoCards(self): self.insertCard(2)

	# Add the listed cards to the just created deck, then close the window.
	def finish(self):
		deckName, hero = getDeckInfo(self.deck_id)
		storeNewCardList(deckName, hero, self.newCardList)
		if self.parent:
			self.parent.destroy()
		self.master.destroy()

	# Add the entered to the cardList, give ButtonArray the new card list, then recreate the ButtonArray and clear text entry.
	def insertCard(self, number):
		addCard((self.cardEntry.get(), number), self.newCardList)
		self.cardButtons.refreshButtons()
		self.cardEntry.delete(0, 'end')

 	# Remove a (single) card from cardList, then recreate the buttons.
	def deleteCard(self, eventCatcher, card):
		onlyOne = (card[0], 1)
		removeCard(onlyOne, self.cardButtons.cardList)
		self.cardButtons.refreshButtons()

# Class for an array of buttons.  Each button displays the name of a card in cardList.
# Clicking a button will perform a provided command, based on mouse click, with the card as input.
class ButtonArray:

	def __init__(self, master, startingList, direction = 'VERT', pos = (5, 5), 
		buttonLeftClick = False,
		buttonRightClick = False,
		buttonMidClick = False
		):

		self.cardList = startingList
		self.master = master
		self.buttons = []
		if buttonLeftClick:
			self.buttonLeftClick = buttonLeftClick
		else:
			self.buttonLeftClick = self.dummy
		if buttonRightClick:
			self.buttonRightClick = buttonRightClick
		else:
			self.buttonRightClick = self.dummy
		if buttonMidClick:
			self.buttonMidClick = buttonMidClick
		else:
			self.buttonMidClick = self.dummy
		self.pos = pos
		self.direction = direction

		self.refreshButtons()

	# Recreate the list of card buttons by destroying all buttons, then adding a button for each card in cardList.
	# Clicking on a card removes it from cardList.
	def refreshButtons(self):
		self.clearButtons()
		for card in self.cardList:
			self.buttons += [Button(self.master, text = singleCardString(card))]
			self.buttons[-1].bind('<Button-1>', partial(self.buttonLeftClick, card = card))			
			self.buttons[-1].bind('<Button-3>', partial(self.buttonRightClick, card = card))
			self.buttons[-1].bind('<Button-2>', partial(self.buttonMidClick, card = card))
		(x, y) = self.pos
		buttonWidth = 150
		buttonHeight = 20
		for button in self.buttons:
			button.place(x = x, y = y, width = buttonWidth, height = buttonHeight)
			if self.direction == 'VERT':
				y += buttonHeight + 5
			elif self.direction == 'HORZ':
				x += buttonWidth + 5

	# Destroy all buttons.
	def clearButtons(self):
		for button in self.buttons:
			button.destroy()
		self.buttons = []

	def dummy(self, card):
		print('You dummy!  I have no idea what you wanted to do with %s!' % card[0])


# Prompt to manually enter a deck name and hero.  Creates the deck if it is a new deck.
class DeckInfoWindow:

	def __init__(self, master, message = ''):

		self.newDeck = StringVar()
		self.newHero = StringVar()
		self.master = master

		self.text0 = Label(master, text = 'Deck Name:')
		self.text0.pack()
		self.text0.place(x = 0, y = 0, height = 25)

		self.text1 = Label(master, text = 'Deck Name:')
		self.text1.pack()
		self.text1.place(x = 0, y = 30, height = 25, width = 75)

		self.text2 = Label(master, text = 'Deck Hero:')
		self.text2.pack()
		self.text2.place(x = 0, y = 60, height = 25, width = 75)

		self.ok = Button(master, text = 'OK', command = self.next)
		self.ok.pack()
		self.ok.place(x = 0, y = 90, height = 55, width = 230)

		self.deckEntry = Entry(master, textvariable = self.newDeck)
		self.deckEntry.pack()
		self.deckEntry.place(x = 80, y = 30, height = 25, width = 150)

		self.heroEntry = Entry(master, textvariable = self.newHero)
		self.heroEntry.pack()
		self.heroEntry.place(x = 80, y = 60, height = 25, width = 150)

	# Open the next window.
	def next(self):
		deckName = self.newDeck.get()
		deckHero = self.newHero.get()
		deck_id = addDeck(deckName, 0, deckHero) # Need to add check if deck already exists - maybe.
		newWindow = Toplevel(self.master)
		dc = DeckCreator(newWindow, deck_id, self.master)

# Display a list of buttons, for each unique deck in the database.
class DeckSelector:

	def __init__(self, master, nextWindow):

		allDecks = getDistinctDecks()
		self.deckButtons = []
		self.nextWindow = nextWindow
		self.master = master

		for deck in allDecks:
			buttonText = '%s (%s)' % (deck[1], deck[2])
			self.deckButtons += [Button(self.master, text = buttonText, command = partial(self.openNextWindow, deck[0]))]

		newY = 5
		buttonHeight = 30
		for button in self.deckButtons:
			button.place(x = 5, y = newY, width = 200, height = buttonHeight)
			newY += buttonHeight		

	# Open the next window, with the selected deck_id.
	def openNextWindow(self, deck_id):
		nextInstance = Toplevel(self.master)
		next = self.nextWindow(nextInstance, deck_id, self.master)

# Display a window that mimmicks a hearthstone game, to track played cards.
class GameTracker:

	def __init__(self, master, deck_id, parent):

		self.master = master
		self.deck_id = deck_id
		self.parent = parent
		self.turn = 0

		self.oppHero = StringVar()

		initialCardList = getCardList(deck_id)
		self.deck = ButtonArray(master, initialCardList,
			buttonLeftClick = self.draw,
			buttonRightClick = partial(self.removeFromDeck, action = 'DISCARD - DECK'),
			buttonMidClick = partial(self.removeFromDeck, action = 'PULL - DECK')
			)
		self.hand = ButtonArray(master, [], direction = 'HORZ', pos = (5, 755),
			buttonLeftClick = partial(self.removeFromHand, action = 'PLAY'),
			buttonRightClick = partial(self.removeFromHand, action = 'DISCARD - HAND'),
			buttonMidClick = partial(self.removeFromHand, action = 'PULL - HAND')
			)

		self.game_id = startGame(deck_id)

		self.turnCounter = Label(master, text = str(self.turn))
		self.turnCounter.pack()
		self.turnCounter.place(x = 600, y =370)

		self.button0 = Button(master, text = 'NEXT TURN', bg = 'yellow', command = self.nextTurn)
		self.button0.pack()
		self.button0.place(x = 600, y = 400, height = 50, width = 205)

		self.button1 = Button(master, text = 'WIN GAME', bg = 'green', command = partial(self.endGame, 1))
		self.button1.pack()
		self.button1.place(x = 600, y = 455, height = 50, width = 100)

		self.button2 = Button(master, text = 'LOSE GAME', bg = 'red', command = partial(self.endGame, 0))
		self.button2.pack()
		self.button2.place(x = 705, y = 455, height = 50, width = 100)

		self.text0 = Label(master, text = 'Opp. Hero:')
		self.text0.pack()
		self.text0.place(x = 175, y = 30, height = 25)

		self.oppHeroEntry = Entry(master)
		self.oppHeroEntry.pack()
		self.oppHeroEntry.place(x = 250, y = 30, height = 25, width = 150)

		self.text1 = Label(master, text = 'Opp. Deck:')
		self.text1.pack()
		self.text1.place(x = 175, y = 60, height = 25)

		self.oppDeckEntry = Entry(master)
		self.oppDeckEntry.pack()
		self.oppDeckEntry.place(x = 250, y = 60, height = 25, width = 150)

		self.text2 = Label(master, text = 'Game Mode:')
		self.text2.pack()
		self.text2.place(x = 175, y = 90, height = 25)

		self.gameModeEntry = Entry(master)
		self.gameModeEntry.pack()
		self.gameModeEntry.place(x = 250, y = 90, height = 25, width = 150)

		self.text3 = Label(master, text = 'Add card:')
		self.text3.pack()
		self.text3.place(x = 500, y = 510, height = 25)

		self.newCard = Entry(master)
		self.newCard.pack()
		self.newCard.place(x = 500, y = 540, height = 25, width = 150)

		self.text4 = Label(master, text = 'Created by:')
		self.text4.pack()
		self.text4.place(x = 500, y = 570, height = 25)

		self.newCardOrigin = Entry(master)
		self.newCardOrigin.pack()
		self.newCardOrigin.place(x = 500, y = 600, height = 25, width = 150)

		self.button3 = Button(master, text = 'ADD TO DECK', bg = 'orange', command = partial(self.createCard, 'DECK'))
		self.button3.pack()
		self.button3.place(x = 655, y = 510, height = 55, width = 100)

		self.button4 = Button(master, text = 'ADD TO HAND', bg = 'blue', command = partial(self.createCard, 'HAND'))
		self.button4.pack()
		self.button4.place(x = 655, y = 570, height = 55, width = 100)


	# Move card from deck to hand.
	def draw(self, eventCatcher, card):
		onlyOne = (card[0], 1)
		removeCard(onlyOne,self.deck.cardList)
		addCard(onlyOne,self.hand.cardList)
		self.deck.refreshButtons()
		self.hand.refreshButtons()
		recordAction(self.game_id, card[0], 'DRAW', self.turn)

	# Remove card from hand, marking as played.
	def removeFromHand(self, eventCatcher, action, card):
		onlyOne = (card[0], 1)
		removeCard(onlyOne,self.hand.cardList)
		self.hand.refreshButtons()
		recordAction(self.game_id, card[0], action, self.turn)

	# Remove a card from your deck, without putting it in your hand.
	def removeFromDeck(self, eventCatcher, action, card):
		onlyOne = (card[0], 1)
		removeCard(onlyOne,self.deck.cardList)
		self.deck.refreshButtons()
		recordAction(self.game_id, card[0], action, self.turn)

	# Advance the turn counter.
	def nextTurn(self):
		self.turn += 1

		self.turnCounter.destroy()

		self.turnCounter = Label(self.master, text = str(self.turn))
		self.turnCounter.pack()
		self.turnCounter.place(x = 600, y =370)

	# Record the result of the game, any information entered in the entry boxes, then close this window, and the parent window.
	def endGame(self, result):
		finishGame(self.game_id, result = result, opponentHero = self.oppHeroEntry.get(), opponentDeck = self.oppDeckEntry.get(), gameMode = self.gameModeEntry.get())
		if self.parent:
			self.parent.destroy()
		self.master.destroy()

	# Add a card to either HAND or DECK.
	def createCard(self, where):
		newCard = self.newCard.get()
		newCardOrigin = self.newCardOrigin.get()
		if newCardOrigin:
			newCardOrigin = ' (%s)' % newCardOrigin
		newCardName = newCard + newCardOrigin
		self.newCard.delete(0, 'end')
		self.newCardOrigin.delete(0, 'end')
		if where == 'HAND':
			addCard((newCardName, 1),self.hand.cardList)
			self.hand.refreshButtons()
		elif where == 'DECK':
			addCard((newCardName, 1),self.deck.cardList)
			self.deck.refreshButtons()
		recordAction(self.game_id, newCardName, 'CREATED - ' + where, self.turn)


# Open a window to view the win-loss record of a particular deck, based on options selected.
class DeckStats:

	def __init__(self, master, deck_id, parent):

		self.master = master
		self.deck_id = deck_id
		self.parent = parent

		self.deck = Deck(deck_id)
		
		self.t = StringVar()

		self.overallRecord = Label(self.master, textvariable = self.t)
		self.overallRecord.pack()
		self.overallRecord.place(x = 5, y = 5, height = 50, width = 100)

		self.options = CheckButtonList(self.master, self.refreshResults,
				[
					{'onvalue' : 'opp_hero'	,	'label' : 'Opposing Hero:'	},
					{'onvalue' : 'opp_deck'	,	'label' : 'Opposing Deck:'	},
					{'onvalue' : 'game_mode',	'label' : 'Game Mode:'		},
					{'onvalue' : 'PLAY'		,	'label' : 'Played Card:'	},
					{'onvalue' : 'DRAW'		,	'label' : 'Drawn Card:'		},
					{'onvalue' : 'CARD REC'	,	'label' : 'Card Record:'	}
				]
			)

		self.refreshResults()

	# Display record based on options selected
	def refreshResults(self):
		conditions = {}
		for i, pressed in enumerate(self.options.pressedButtons):
			if pressed.get():
				conditions[pressed.get()] = self.options.entryFields[i].get()
		self.t.set('Wins:     %s\nLosses:   %s' % self.deck.getCardRecord(conditions))


# Accept a list of {label : '', on_value : ''} dicts to create a multi-selection checkbutton list.
class CheckButtonList:

	def __init__(self, master, function, selections):

		self.pressedButtons = []
		self.choiceButtons = []
		self.entryFields = []
		self.columnHeaders = []

		width = 125
		height = 25
		x = 200
		y = 5

		for i, selection in enumerate(selections):

			self.pressedButtons += [StringVar()]
			self.choiceButtons += [Checkbutton(master, text = selection['label'], command = function, var = self.pressedButtons[i], onvalue = selection['onvalue'], offvalue = '', anchor = W)]
			self.entryFields += [Entry(master)]

		for i in range(len(self.choiceButtons)):
			self.choiceButtons[i].place(x = x, y = y, width = width, height = height)
			self.entryFields[i].place(x = x + width, y = y, width = width, height = height)
			y += height + 5

root = Tk()
app = MainWindow(root)
root.mainloop()