# Return True or False, based on input of "y" or "n".
def getYesOrNo(message):
	while True:
		response = input(message)
		if response == 'y':
			return True
		elif response == 'n':
			return False
		else:
			print('Invalid input!')

# Ensure an integer (within range) is returned from an input prompt.  Otherwise, return False.
def getIntOrFalse(message, minimum = 0, maximum = False):
	value = input(message)
	try:
		value = int(value)
	except:
		return False
	else:
		if not maximum:
			maximum = value
		if minimum <= value <= maximum:
			return value
		else:
			print('Invalid input!')
			return False