#ASGN3

#!/usr/bin/python
import os
import glob
import nltk
''' ... START Global Data Structures ... '''
from nltk.tokenize import sent_tokenize, word_tokenize, wordpunct_tokenize
from nltk.stem.porter import PorterStemmer #Note: stem not stemmer - https://www.google.com.sg/search?q=NLTK+Porter+stemmer+import   #http://www.ibm.com/developerworks/library/l-cpnltk/index.html

import math

import time

import getopt
import sys

#debug=1

##Changes: Check for docFreq



class PostingSmall:
    def __init__(self, logFreqWeight = 0.0):
        #self.docID = docID
        self.logFreqWeight = logFreqWeight  #Calc in FINAL. CANNOT BE ZERO!! MUST BE FLOAT!!
        self.lengthNormalization = 0.0
    #Normalization can't be calculated here. Requires ALL QUERY TERMS, hence must be done outside.
    def toString_wHeaders(self):
        return "(id" +str(self.docID)+ ", tf" +str(self.termFreq)+ ", weight" +str(self.logFreqWeight)+"&"+str(self.TfxIdf)+ ")"
    def toString_forWrite(self):
        return str(self.logFreqWeight) ##+ ":" +str(self.TfxIdf)   ##+ ":" +str(self.termFreq)
#end of the class


#For QueryTerms
def getDocIDs(file_inPostingsLists, pointer, lengthRead):
    file_inPostingsLists.seek(int(pointer));
    docIDs = file_inPostingsLists.read(int(lengthRead)) #to prevent reading all the way to end
    return [int(docID) for docID in docIDs.split()]

def getPostings(file_inPostingsLists, pointer, lengthRead):
    file_inPostingsLists.seek(int(pointer));
    postingsListRaw = file_inPostingsLists.read(int(lengthRead)) #to prevent reading all the way to end
    postingsList = {}
    for eachPostingRaw in postingsListRaw.split():
        docID, logFreqWeight = eachPostingRaw.split(':')
        docID = int(docID)
        logFreqWeight = float(logFreqWeight)
        postingsList[docID] = PostingSmall(logFreqWeight)
    return postingsList

class DictionaryTermSmall: #Token-DocID PairF
    def __init__(self, token, invDocFreq=0.0, ptr=0, lengthRead=0): #SYNT: make some parameters optional by providing default values
        self.token = token  #Should correspond with the key outside of this class
        #self.freq  = freq
        self.invDocFreq = invDocFreq #the docFreq of unique docIDs
        self.ptr   = ptr
        self.lengthRead = lengthRead
    def printString(self):
        print str(self.token)+":\tinvDocFreq",str(self.docFreq), ' ptr',str(self.ptr), str(self.lengthRead)

class QueryTerm: #Token-DocID PairF
    def __init__(self, dictList, token, file_inPostingsLists, termFreq=0): #SYNT: make some parameters optional by providing default values
        ##The .lower() is now done outside. For sure since it is only at once location.
        #token = token.lower() #Convert to lowercase in case the value passed it is not lowercase
        self.token = token
        self.invDocFreq = float(dictList[token].invDocFreq) #the docFreq of unique docIDs
        #self.ptr   = dictList[token].ptr
        #self.lengthRead = dictList[token].lengthRead

        #---The Postings taken from Dictionary, will be used for matching with Query.
        self.postings = {}
        self.postings = getPostings(file_inPostingsLists, dictList[token].ptr, dictList[token].lengthRead)

        #---PostingSmall FOR QUERY, treating Query as ONE doc--- Transplanted here
        self.termFreq = termFreq #When you create it, you start off with 1.
        self.logFreqWeight = 0.0
        self.TfxIdf = 0.0
        self.vectorLength = 0.0
        self.lengthNormalization = 0.0

    def calc_logFreqWeight(self):
        if self.termFreq>0: #To avoid ERROR due to Log(ZERO).
            self.logFreqWeight = 1.0+ math.log10(self.termFreq) #ALT: math.log10(self.termFreq) vs math.log(self.termFreq, 10)
        elif self.termFreq<=0:
            self.logFreqWeight = 0.0
        return self.logFreqWeight ##Change in code struct. Now using return value in calc_TfxIdf  ## Not really necessary since this function is called during indexing. During searching, the direct variable is used, and this function is NOT called.
    def calc_TfxIdf(self):  ###(self, invDocFreq_from_DictionaryTerm_class):
        self.TfxIdf = self.calc_logFreqWeight() * self.invDocFreq ###invDocFreq_from_DictionaryTerm_class #Both of them are CONFIRMED Floats already.
        #return self.TfxIdf

    def calcDerivatives(self): #7769 is Total Count of Reuters Documents in Folder
#        if totalUniqueDocCount != 7769: print "WARNING: Total Unique Doc Count is", totalUniqueDocCount, " and is NOT 7769!!"
        self.calc_TfxIdf()
        #Normalization can't be calculated here. Requires ALL QUERY TERMS, hence must be done outside.

    def printString(self):
        print str(self.token)+":\t invDocFreq",str(self.invDocFreq), str(self.postings)
    def toString_Results(self):
        theToString = '' #Need to assign first before you can do += in the loop part. Else UnboundLocalError.
        #theToString += str(self.token) + ' '  #WARNING: only enable for debugging - to see if postings match dict
        for eachDocID in self.docIDs:
            theToString += str(eachDocID) + ' '
        return theToString

    def toString_PListsRanked(self): #For postings[] instead of docIDs[]
        theToString = '' #Need to assign first before you can do += in the loop part. Else UnboundLocalError.
        theToString += str(self.token) + ' '  #WARNING: only enable for debugging - to see if postings match dict
        for eachPosKey in sorted(self.postings):
            theToString += str(eachPosKey)+":"+self.postings[eachPosKey].toString_forWrite() + ' '
        return theToString

class docMatchResult:
    def __init__(self, docID, vectorLength=0.0):
        #self.docID = docID
        self.vectorLength = vectorLength #vectorLength is SquareRoot of sum of squares
        self.cosineScore = 0.0
#end of class docMatchResult

#===========================================================================
#The MAIN function
def startAnalysis(inFile_queries, outFile_results, inFile_dictionary='dictionary.txt', inFile_postingsLists='postings.txt'):
    #debug=1
    #if debug==1: startTime = time.time()
    file_inQueries = 'queries.txt' ##NOTE
#Create dictList
    file_inDictionary = open(inFile_dictionary, 'r')
    dictList = {}
    for eachDictLine in file_inDictionary:
        tokenName, docFreq, pointer, lengthRead = eachDictLine.split(' ', 3)
        dictList[tokenName] = DictionaryTermSmall(tokenName,docFreq, pointer,lengthRead)
        #No need to check if exist before, because the Dict is SUPPOSED to be UNIQUE already
#Create fullDocList
    file_inFullDocList = open("fullDocList.txt", 'r')
    fullDocList = []
    for docID_value in file_inFullDocList.read().split():
        #if debug==1: print docID_value
        fullDocList.append(int(docID_value))
#Analyse Queries
    file_inPostingsLists = open(inFile_postingsLists, 'r') #Comment out once stable
    file_inQueries = open(inFile_queries, 'r')
    file_outResults = open(outFile_results, 'w')
    #if debug==1: queryLineNum = 0
    for eachQueryLine in file_inQueries:
        #if debug==1: queryLineNum += 1
        #if debug==1: print "opening query line number " +str(queryLineNum)+ "..."
        tokenizedSentences = sent_tokenize(eachQueryLine)
        #if debug==1: print "Sentences", tokenizedSentences
        tokenizedWords = [word_tokenize(eachSentence) for eachSentence in tokenizedSentences]
        #if debug==1: print "Words:", tokenizedWords
        queTokens = {} #Switch to dict instead of list. Don't need position. But need check if exist already - hence dict keys.
        docsToBeCompared = {} ##NEW!!
        for eachTuple in tokenizedWords:
            for eachTerm in eachTuple: ##eachTerm is a eachWord
                #if debug==1: print eachTerm
                ###if eachTerm!="(" or eachTerm!=")" or eachTerm!="NOT" or eachTerm!="AND" or eachTerm!="OR":
                stemmedTerm = PorterStemmer().stem_word(eachTerm)
                #if debug==1: print stemmedTerm
                finalTerm = stemmedTerm.lower()

                #Now there are 3 cases:
                #(1) first occurence across all docs
                #(2) first occurence within THIS doc
                #(3) subsequent occurence within this doc
                if finalTerm not in queTokens.keys(): #First occurence across all docs.
                    queTokens[finalTerm] = QueryTerm(dictList,finalTerm, file_inPostingsLists, termFreq=1)
                    #This is creation. Frequency already "incremented" during creation.
                    for eachDocNeeded in queTokens[finalTerm].postings.keys():
                        if eachDocNeeded not in docsToBeCompared.keys():
                            docsToBeCompared[eachDocNeeded] = docMatchResult(eachDocNeeded)
                else:
                    #Do not append since this is not new docID.
                    queTokens[finalToken].postings[docID].termFreq += 1  #array[-1] to access LAST element that was most recently appended
                    #pass
        #if debug==1: print queTokens
        #===Calculate the Cosines===
        #First need to do length Normalization  ###def calc_lengthNormalizations_inPostingsList(queTokens):

        #docMatchResultsList is docsToBeCompared
        vectorLength = 0.0 #vectorLength is SquareRoot of sum of squares
        for eachKey in queTokens.keys():
            queTokens[eachKey].calcDerivatives()
        #Need all Tokens to be readied first. It has been readied by step above.
        #Now NORMALIZE for document called QUERY
        for eachKey in queTokens.keys():
            queTokens[eachKey].vectorLength = 0.0
            for eachSubKey in queTokens.keys():
                queTokens[eachKey].vectorLength += math.pow(queTokens[eachKey].TfxIdf, 2)
            #once we have gone through all values, we need to square root
            queTokens[eachKey].vectorLength = math.sqrt(queTokens[eachKey].vectorLength)
            queTokens[eachKey].lengthNormalization = queTokens[eachKey].TfxIdf / queTokens[eachKey].vectorLength

        #Now NORMALIZE for all other documentS in documents list
        for eachDocN in docsToBeCompared.keys():
            docsToBeCompared[eachDocN].vectorLength = 0.0
            docsToBeCompared[eachDocN].cosineScore = 0.0
            for eachToken in queTokens.keys():
                if eachDocN not in queTokens[eachToken].postings.keys():
                    docsToBeCompared[eachDocN].vectorLength += 0.0
                elif queTokens[eachToken].postings[eachDocN].logFreqWeight > 0:
                    tmpLFW = queTokens[eachToken].postings[eachDocN].logFreqWeight
                    docsToBeCompared[eachDocN].vectorLength += math.pow(tmpLFW, 2)
            #once we have gone through all values, we need to square root
            docsToBeCompared[eachDocN].vectorLength = math.sqrt(docsToBeCompared[eachDocN].vectorLength)

            #now let's find lengthNormalization for each term AND then get the CosineScore!!
            for eachToken in queTokens.keys():
                if eachDocN not in queTokens[eachToken].postings.keys(): #SIMILAR TO ABOVE
                    #normalizedLength_fromDoc = 0.0 ##redundant
                    #addnlScore = queTokens[eachKey].lengthNormalization * normalizedLength_fromDoc #redundant
                    addnlScore = 0.0
                else:
                    normalizedLength_fromDoc = queTokens[eachToken].postings[eachDocN].logFreqWeight / docsToBeCompared[eachDocN].vectorLength
                    addnlScore = queTokens[eachKey].lengthNormalization * normalizedLength_fromDoc
                docsToBeCompared[eachDocN].cosineScore += addnlScore
        #Now, I have obtained all scores for each document
        docs_sortedbyScores = {}
        for docN, theMatchResult in docsToBeCompared.iteritems():
            docs_sortedbyScores[theMatchResult.cosineScore] = docN
        iCount = 0
        #theScores = []
        theResults_docsList = []
        theResultString = ""
        prevScore = 0.0
        needRearrange = False
        startIndexForRearrangement = 0
        endIndexForRearrangement = 0
        for eachScoreKey in sorted(docs_sortedbyScores):
            if iCount<10:
                #theScores.append(eachScoreKey)
                theResults_docsList.append(docs_sortedbyScores[eachScoreKey])
                if eachScoreKey == prevScore:
                    if needRearrange == False: #First occurence for this relevance value
                        needRearrange = True
                        if (iCount - 1)>=0: startIndexForRearrangement = iCount-1
                        elif (iCount - 1)<0: startIndexForRearrangement = 0  #In case first relevance is 0.0
                    else: #if needRearrange continues to be True
                        pass #doNothing
                elif eachScoreKey != prevScore:
                    if needRearrange == False: #the typical case
                        theResultString += str(docs_sortedbyScores[eachScoreKey]) +' '
                    elif needRearrange == True:
                        #This means the previous strings of scores were the same. Need to rearrange by increasing documentID.
                        endIndexForRearrangement = iCount-1;
                        tmpArrayForRearragenment = []
                        for tmpIndex in range(startIndexForRearrangement, endIndexForRearrangement+1):
                            tmpArrayForRearragenment.append(theResults_docsList[tmpIndex])
                        tmpArrayForRearragenment.sort()
                        theResults_docsList[startIndexForRearrangement:endIndexForRearrangement+1] = tmpArrayForRearragenment
                        for eachDocN in tmpArrayForRearragenment:
                            theResultString += str(eachDocN)
                        needRearrange = False
                iCount += 1
            else: #if iCount>=10
                break  #stop the for eachScoreKey
        #theResultString += '\n'
        #for eachDocN in theResults_docsList:
        #    theResultString += str(eachDocN) +' '
        print >> file_outResults, theResultString
    #end of for eachQueryLine
    #if debug==1: print "Total Time Elapsed:", time.time()-startTime
#end of function startAnalysis()

#==================================================
def usage():
    print "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"

inFile_dictionary = inFile_postingsLists = inFile_queries = outFile_results = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-d':
        inFile_dictionary = a
    elif o == '-p':
        inFile_postingsLists = a
    elif o == '-q':
        inFile_queries = a
    elif o == '-o':
        outFile_results = a
    else:
        assert False, "unhandled option"
if inFile_dictionary == None or inFile_postingsLists == None or inFile_queries == None or outFile_results == None:
    usage()
    sys.exit(2)
#==================================================
startAnalysis(inFile_queries, outFile_results, inFile_dictionary, inFile_postingsLists)
#test_Dict_PLists('finalDictionary.txt', 'finalPostings.txt')
#python search.py -d dictionary.txt -p postings.txt -q queries.txt -o finalSearchResults.txt

