from tkinter import *
from deckManagement import *
from deckManagementPrompts import *
from functools import partial

# Class for the inital window.  Has buttons to go to EDIT DECK or NEW DECK.
class MainWindow:

	def __init__(self, master):

		self.master = master

		frame = Frame(master)
		frame.pack()

		self.button = Button(frame, text = 'NEW DECK', fg = 'red', command = self.newDeck)
		self.button.pack(side = LEFT)

		self.hi_there = Button(frame, text = 'EDIT DECK', command = self.editDeck)
		self.hi_there.pack(side = LEFT)

	def newDeck(self):
		newWindow = Toplevel(self.master)
		di = DeckInfoWindow(newWindow, message = 'Enter the name and hero of a new deck!', new = True)
		 # Need to add check if exists later.

	def editDeck(self):
		newWindow = Toplevel(self.master)
		di = DeckInfoWindow(newWindow, message = "Enter the name and hero of deck you'd like to edit!", new = False)

# Class for the window to edit a deck.  Enter a card name in the text box, then either "ADD 1" or "ADD 2".
# When done, hit "DONE" to add the deck into the database and close the window.
class DeckCreator:

	def __init__(self, master, deck_id, parent = False, new = False):

		self.listDisplay = StringVar()
		if new:
			self.newCardList = []
		else:
			self.newCardList = getCardList(deck_id)
		self.deck_id = deck_id
		self.master = master
		self.parent = parent
		self.new = new

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

		self.cardButtons = ButtonArray(master, self, self.newCardList)

	# Wrappers for inserting either 1 or two cards.
	def addOneCard(self): self.insertCard(1)
	def addTwoCards(self): self.insertCard(2)

	# Add the listed cards to the just created deck, then close the window.
	def finish(self):
		if self.new:
			addCards(self.deck_id, self.newCardList)
		else:
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

# Class for an array of buttons.  Each button displays the name of a card in cardList.
class ButtonArray:

	def __init__(self, master, parent, startingList):

		self.cardList = startingList
		self.master = master
		self.parent = parent
		self.buttons = []

		self.refreshButtons()

	# Remove a card from cardList, then recreate the buttons.
	def deleteCard(self, card):
		removeCard(card,self.cardList)
		self.refreshButtons()

	# Recreate the list of card buttons by destroying all buttons, then adding a button for each card in cardList.
	# Clicking on a card removes it from cardList.
	def refreshButtons(self):
		self.clearButtons()
		for card in self.cardList:
			self.buttons += [Button(self.master, text = singleCardString(card), command = partial(self.deleteCard, card))]
		newY = 75
		buttonHeight = 30
		for button in self.buttons:
			button.place(x = 5, y = newY, width = 150, height = buttonHeight)
			newY += buttonHeight

	# Destroy all buttons.
	def clearButtons(self):
		for button in self.buttons:
			button.destroy()
		self.buttons = []


class DeckInfoWindow:

	def __init__(self, master, message = '', new = False):

		self.newDeck = StringVar()
		self.newHero = StringVar()
		self.master = master
		self.new = new

		self.text1 = Label(master, text = 'Deck Name:')
		self.text1.pack()
		self.text1.place(x = 0, y = 0, height = 25, width = 75)

		self.text2 = Label(master, text = 'Deck Hero:')
		self.text2.pack()
		self.text2.place(x = 0, y = 30, height = 25, width = 75)

		self.ok = Button(master, text = 'OK', command = self.next)
		self.ok.pack()
		self.ok.place(x = 0, y = 60, height = 55, width = 230)

		self.deckEntry = Entry(master, textvariable = self.newDeck)
		self.deckEntry.pack()
		self.deckEntry.place(x = 80, y = 0, height = 25, width = 150)

		self.heroEntry = Entry(master, textvariable = self.newHero)
		self.heroEntry.pack()
		self.heroEntry.place(x = 80, y = 30, height = 25, width = 150)

	def next(self):
		deckName = self.newDeck.get()
		deckHero = self.newHero.get()
		if self.new:
			deck_id = addDeck(deckName, 0, deckHero)
		else:
			deck_id = getDecks(deckName, deckHero)
		newWindow = Tk()
		dc = DeckCreator(newWindow, deck_id, self.master, self.new)

root = Tk()

app = MainWindow(root)

root.mainloop()