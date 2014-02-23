#!/usr/bin/python
import os
import glob
import nltk
''' ... START Global Data Structures ... '''
from nltk.tokenize import sent_tokenize, word_tokenize, wordpunct_tokenize
from nltk.stem.porter import PorterStemmer #Note: stem not stemmer - https://www.google.com.sg/search?q=NLTK+Porter+stemmer+import   #http://www.ibm.com/developerworks/library/l-cpnltk/index.html

import time

import getopt
import sys

debug=1

#For QueryTerms
def getDocIDs(file_inPostingsLists, pointer, lengthRead):
    file_inPostingsLists.seek(int(pointer));
    docIDs = file_inPostingsLists.read(int(lengthRead)) #to prevent reading all the way to end
    return [int(docID) for docID in docIDs.split()]

class DictionaryTermSmall: #Token-DocID PairF
    def __init__(self, token, docFreq=1, ptr=0, lengthRead=0): #SYNT: make some parameters optional by providing default values
        self.token = token  #Should correspond with the key outside of this class
        #self.freq  = freq
        self.docFreq = docFreq #the docFreq of unique docIDs
        self.ptr   = ptr
        self.lengthRead = lengthRead
    def printString(self):
        print str(self.token)+":\tfreq",str(self.docFreq), ' ptr',str(self.ptr), str(self.lengthRead)

class QueryTerm: #Token-DocID PairF
    def __init__(self, dictList, token, file_inPostingsLists): #SYNT: make some parameters optional by providing default values
        token = token.lower() #Convert to lowercase in case the value passed it is not lowercase
        self.token = token
        self.docFreq = dictList[token].docFreq #the docFreq of unique docIDs
        #self.ptr   = dictList[token].ptr
        #self.lengthRead = dictList[token].lengthRead
        self.docIDs = getDocIDs(file_inPostingsLists, dictList[token].ptr, dictList[token].lengthRead)  #NO LONGER just another empty array
    def printString(self):
        print str(self.token)+":\t docFreq",str(self.docFreq), str(self.docIDs)
    def toString_Results(self):
        theToString = '' #Need to assign first before you can do += in the loop part. Else UnboundLocalError.
        #theToString += str(self.token) + ' '  #WARNING: only enable for debugging - to see if postings match dict
        for eachDocID in self.docIDs:
            theToString += str(eachDocID) + ' '
        return theToString

class ResolvedQueryTerm: #Token-DocID PairF
    def __init__(self, docIDs): #SYNT: make some parameters optional by providing default values
        self.token = "!!!"
        self.docFreq = len(docIDs) #the docFreq of unique docIDs
        #self.ptr   = dictList[token].ptr
        #self.lengthRead = dictList[token].lengthRead
        self.docIDs = docIDs  #NO LONGER just another empty array
    def printString(self):
        print str(self.token)+":\t docFreq",str(self.docFreq), str(self.docIDs)
    def toString_Results(self):
        theToString = '' #Need to assign first before you can do += in the loop part. Else UnboundLocalError.
        #theToString += str(self.token) + ' '  #WARNING: only enable for debugging - to see if postings match dict
        for eachDocID in self.docIDs:
            theToString += str(eachDocID) + ' '
        return theToString

def test_Dict_PLists(outFile_dictionary='dictionary.txt', outFile_postingsLists='postings.txt'):
    print '='*10 + 'Test Dict PLists' + '='*10
    print outFile_dictionary
    dictionary = open(outFile_dictionary, 'r')
    postingsLists = open(outFile_postingsLists, 'r')
    print dictionary
    #test = [1,2,3]
    #for ea in test:
    #    print ea
    for eachDictLine in dictionary:
        print "DICT LINE: " +eachDictLine
        tokenName, freqCount, pointer, lengthOfRead = eachDictLine.split(' ', 3)
        print "after split: " +tokenName, freqCount, pointer, lengthOfRead
        postingsLists.seek(int(pointer));
        postingsValues = postingsLists.read(int(lengthOfRead)) #to prevent reading all the way to end
        print "POSTINGS LIST: " +postingsValues
#end of function test_Dict_PLists
#personal note: interesting. within function. hm.

#===========================================================================
#===== The MERGE functions =====
#For analyzeInterior() to use
#which is within startAnalysis()
def printResolvedMsg(queTokens):
    thePrintMsg = ''
    for i in range(len(queTokens)):
        if (queTokens[i].token):
            thePrintMsg += str(queTokens[i].token)+ ' '
        else:
            thePrintMsg += str(queTokens[i])+ ' '
    print thePrintMsg

def mergeNOT(queTerm, fullDocList): #queTerm1 should be the smaller one
    newDocList = []
    list1 = queTerm.docIDs
    i=0; j=0
    while i!=len(list1) and j!=len(fullDocList): #Logic: j will in the end be bigger than i. Hence need to make up for j later.
        if list1[i]==fullDocList[j]:
            i+=1; j+=1;
        elif list1[i]<fullDocList[j]:
            i+=1
        elif fullDocList[j]<list1[i]:
            newDocList.append(fullDocList[j])
            j+=1
    while j!=len(fullDocList):
        newDocList.append(fullDocList[j])
        j+=1
    return ResolvedQueryTerm(newDocList)

def mergeAND(queTerm1, queTerm2): #queTerm1 should be the smaller one
    #debug=1
    newDocList = []
    list1 = queTerm1.docIDs
    list2 = queTerm2.docIDs
    i=0; j=0
    while i!=len(list1) and j!=len(list2):
        if list1[i]==list2[j]:
            newDocList.append(list1[i])
            i+=1; j+=1;
        elif list1[i]<list2[j]:
            i+=1
        elif list2[j]<list1[i]:
            j+=1
    #if debug==1: printResolvedMsg([queTerm1,"AND",queTerm2])
    #print "resolved AND"
    return ResolvedQueryTerm(newDocList)

def mergeOR(queTerm1, queTerm2): #queTerm1 should be the smaller one
    #debug=1
    newDocList = []
    list1 = queTerm1.docIDs
    list2 = queTerm2.docIDs
    i=0; j=0
    while i!=len(list1) and j!=len(list2):
        if list1[i]==list2[j]:
            newDocList.append(list1[i])
            i+=1; j+=1;
        elif list1[i]<list2[j]:
            newDocList.append(list1[i])
            i+=1
        elif list2[j]<list1[i]:
            newDocList.append(list2[j])
            j+=1
    if len(list1)>len(list2):
        while i!=len(list1):
            newDocList.append(list1[i])
            i+=1
    elif len(list2)>len(list1):
        while j!=len(list2):
            newDocList.append(list2[j])
            j+=1
    #if debug==1: printResolvedMsg([queTerm1,"OR",queTerm2])
    print "resolved OR"
    return ResolvedQueryTerm(newDocList)

#===========================================================================
#For startAnalysis() to use

def analyzeInterior(queTokens, fullDocList):
    #debug=1
#Resolve all the NOT
    while "NOT" in queTokens:
        startInd = queTokens.index("NOT")
        endInd = startInd+1
        currInd = endInd
        numNOTs = 1
        while queTokens[currInd] == "NOT":
            currInd += 1
            numNOTS += 1
        endInd = currInd
        if numNOTs%2!=0: #Means it is odd, perform a "NOT" operation
            #OLD VER, before Insert was created ==> del queTokens[startInd:endInd+1]
            newResolvedTerm = mergeNOT(queTerm, fullDocList) #merge with fullDocList
            queTokens.insert(startInd, newResolvedTerm)
            #if debug==1: printResolvedMsg(queTokens[startInd+1:endInd+2])
            del queTokens[startInd+1:endInd+2]
        elif numNOTs%2==0: #Means it is even, delete all the NOTs, and don't apply NOT to the term
            #if debug==1: printResolvedMsg(queTokens[startInd:endInd])
            del queTokens[startInd:endInd] #No plus one because should not affect the term
#Resolve all the "AND"
    while "AND" in queTokens: #All the brackets and NOT should be resolved and removed by now
        startInd = queTokens.index("AND")
        currInd = startInd+1 #this touches the next TERM
        consecTerms = []
        consecTerms.append(queTokens[startInd-1]) #Append the 1st TERM on the LHS of AND
        consecTerms.append(0); #to keep in step with original consecTerms index
        while queTokens[currInd+1]=="AND": #With another +1, it now touches the next "AND" if any
            consecTerms.append(queTokens[currInd])
            consecTerms.append(0)
            currInd += 2 #It's not +1 because the next one is AND.
        endInd = currInd
        consecTerms.append(queTokens[currInd]) #Append the last TERM on RHS of AND since it's J AND K AND L OR M
        #then you compare and find the smallest
        minInd = consecTerms.index(min(consecTerms))
        #Then you determine whether leftside or rightside is the next SMALLER one
        if consecTerms[minInd-2] < consecTerms[minInd+2]:
            newStartInd = startInd + (minInd-1) -2;  #merge the earlier LHS
            newEndInd   = startInd + (minInd-1)
        elif consecTerms[minInd-2] > consecTerms[minInd+2]:
            newStartInd = startInd + (minInd-1)
            newEndInd   = startInd + (minInd-1) +2;  #merge the latter RHS
        #OLDER ver, before OLD VER ==> del queTokens[startInd-1:endInd]
        #OLD VER, before Insert was created ==> del queTokens[newStartInd:newEndInd+1]
        newResolvedTerm = mergeAND(queTokens[newStartInd], queTokens[newEndInd])
        queTokens.insert(newStartInd, newResolvedTerm)
        del queTokens[newStartInd+1:newEndInd+2]
#Resolve all the "OR" -- similar
    while "OR" in queTokens:
        startInd = queTokens.index("OR")
        currInd = startInd+1 #this touches the next TERM
        consecTerms = []
        consecTerms.append(queTokens[startInd-1]) #Append the 1st TERM on the LHS of AND
        consecTerms.append(0); #to keep in step with original consecTerms index
        while queTokens[currInd+1]=="OR": #With another +1, it now touches the next "AND" if any
            consecTerms.append(queTokens[currInd])
            consecTerms.append(0)
            currInd += 2 #It's not +1 because the next one is AND.
        endInd = currInd
        consecTerms.append(queTokens[currInd]) #Append the last TERM on RHS of AND since it's J AND K AND L OR M
        #then you compare and find the smallest
        minInd = consecTerms.index(min(consecTerms))
        #Then you determine whether leftside or rightside is the next SMALLER one
        if consecTerms[minInd-2] < consecTerms[minInd+2]:
            newStartInd = startInd + (minInd-1) -2;  #merge the earlier LHS
            newEndInd   = startInd + (minInd-1)
        elif consecTerms[minInd-2] > consecTerms[minInd+2]:
            newStartInd = startInd + (minInd-1)
            newEndInd   = startInd + (minInd-1) +2;  #merge the latter RHS
        #OLDER ver, before OLD VER ==> del queTokens[startInd-1:endInd]
        #OLD VER, before Insert was created ==> del queTokens[newStartInd:newEndInd+1]
        newResolvedTerm = mergeOR(queTokens[newStartInd], queTokens[newEndInd])
        queTokens.insert(newStartInd, newResolvedTerm)
        del queTokens[newStartInd+1:newEndInd+2]
#In the end, we are left with just one term
    return queTokens #The resolved and condensed QueryTerm, derived from the many original QueryTerms
#end of analyzeInterior()

#===========================================================================
#The MAIN function
def startAnalysis(inFile_queries, outFile_results, inFile_dictionary='dictionary.txt', inFile_postingsLists='postings.txt'):
    debug=1
    if debug==1: startTime = time.time()
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
    if debug==1: queryLineNum = 0
    for eachQueryLine in file_inQueries:
        if debug==1: queryLineNum += 1
        if debug==1: print "opening query line number " +str(queryLineNum)+ "..."
        tmpQueTokens = word_tokenize(eachQueryLine)
        if debug==1: print tmpQueTokens
        queTokens = []
        for eachTerm in tmpQueTokens:
            if debug==1: print eachTerm
            if eachTerm!="(" or eachTerm!=")" or eachTerm!="NOT" or eachTerm!="AND" or eachTerm!="OR":
                stemmedTerm = PorterStemmer().stem_word(eachTerm)
                if debug==1: print stemmedTerm
                createQueryTerm = QueryTerm(dictList, stemmedTerm.lower(), file_inPostingsLists)
                queTokens.append(createQueryTerm)
            else:
                queTokens.append(eachTerm);
        if debug==1: print queTokens
#Resolve all the BRACKETS "(" and ")"
#        for i in range(0, len(spQur)):
#            if spQur[i][0] == '(':  #Get 1st one chars: http://docs.python.org/release/1.5.1p1/tut/strings.html
#                if spQur[i][-1] != ')':
#                    analyzeInterior(spQur[])
#Resolve all the BRACKETS "(" and ")"
        while "(" in queTokens:
            startInd = queTokens.index("(")
            endInd = queTokens.index(")")
            #OLD VER, before Insert was created ==> del queTokens[startInd:endInd+1]
            newResolvedBracketTerm = analyzeInterior(queTokens[startInd:endInd+1], fullDocList)
            queTokens.insert(startInd, newResolvedBracketTerm)
            del queTokens[startInd+1:endInd+2]
            if debug==1: print "resolved a BRACKET set"
#Once there are no more brackets, we can do regular interior analysis
        noMoreBrackets_newResolvedTerm = analyzeInterior(queTokens, fullDocList)
        #The end result should be ONE element in List that is from the class of ResolvedQueryTerm.
        print >> file_outResults, noMoreBrackets_newResolvedTerm[0].toString_Results() #SYNTax: Cannot do a + string behind a string here. The plused part wont be written!!
    #end of for eachQueryLine
    if debug==1: print "Total Time Elapsed:", time.time()-startTime
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
#python search.py -d finalDictionary.txt -p finalPostings.txt -q queries.txt -o finalSearchResults.txt

