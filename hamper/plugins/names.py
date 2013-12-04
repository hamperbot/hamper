import random
import re
from datetime import datetime
from hamper.interfaces import ChatCommandPlugin, Command

class Names(ChatCommandPlugin):
	'''Random Name Generator: !name to generate a random name'''
	name = 'names'
	priority = 0
	class Names(Command):
		regex = r'^names$'
		name = 'names'
		def command(self, bot, comm, groups):
			l1 = ["Pixelated ", "Linus ", "Mr.", "Doctor ", "Fernando ", "Bacon ", "Mario ", "Professor ", "Velociraptor ", "Baby monkey ", "Richard ", "Luigi ", "Peach ", "Batman ", "Macafee ", "Mozilla ", "Luxe ", "Yoshi ", "Uzbekistan ", "Stanley ", "Stefon ", "Ayn ", "Hans ", "Hipster ", "Cueball ", "YOLO ", "Hamper ", "Lady ", "Radnall ", "Stephen ", "HP ", "Stud " ]
			l2 = ["Octocat", "McGee", "Fiddlesticks", "Torvalds", "Munroe", "Kitten", "Muffin", "Rasta Primavera", "Fiddlesticks", "Dangerzone", "Jobs", "Stallman", "Moneybags", "Muffin", "Heisenberg", "Zaboomafoo", "Honey", "Fox", "Hawking", "Lovecraft", "Rand", "Vim", "the 34th"]
			name1 = random.randint(0,(len(l1)-1))
			name2 = random.randint(0,(len(l2)-1))
			bot.reply(comm, str(l1[int(name1)])+str(l2[int(name2)]))

names = Names()	
