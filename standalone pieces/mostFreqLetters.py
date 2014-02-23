import urllib
from lxml import html

the_url = "http://www.giwersworld.org/computers/linux/common-words.phtml"
the_htmltag = "pre"

def getWordsList(string):
	return [word.upper() for word in string.rstrip().split("\n")]

def addWordsToDict(lettersDict, wordsList):
	for word in wordsList:
		lettersDict = addLetterToDict(lettersDict, word)
	return lettersDict

def addLetterToDict(lettersDict, string):
	for char in string:
		if char not in lettersDict.keys():
			lettersDict[char] = 1;
		else:
			lettersDict[char] += 1;
	return lettersDict;

def getTopFreqLetters(lettersDict, topX):
	descendingTuples = sorted(  [(val,key) for key,val in lettersDict.items()], reverse=True  );
	topDescendingLetters = [  tup[1] for tup in descendingTuples[:topX]  ];
	dbg.e(1, "\n".join([str(tup) for tup in descendingTuples])  )
	return topDescendingLetters;

#==========
class debugger:
	def __init__(self, starting_value=0):
		self.debug = starting_value;
	def e(self, num, printout):
		if self.debug==num:
			print printout
			return True
		else:
			return False
dbg = debugger(0);

#==========
#req = urllib2.request(the_url)
htmlCode = urllib.urlopen(the_url).read()
docObj = html.fromstring(htmlCode)

for preObj in docObj.xpath("//"+the_htmltag): #There's only one element, but it's a list anyway.
	wordsList = getWordsList(preObj.text)
	lettersDict = addWordsToDict({}, wordsList)
	top10letters = " ".join( getTopFreqLetters(lettersDict,10) )
	print top10letters




