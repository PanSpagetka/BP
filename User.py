class User:
	def __init__(self, username, password):
		self.username = username
		self.password = password

def loadFromFile(filename):
	file = open(filename,"r")
	users = {}
	for line in file:
		parts = line.split()
		if len(parts) == 2:
			users[parts[0]] = User(parts[0], parts[1])
	file.close()
	return users
