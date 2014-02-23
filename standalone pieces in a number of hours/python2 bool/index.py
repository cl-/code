#!/usr/bin/python
import os
import glob
import nltk
#from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tokenize import sent_tokenize, word_tokenize, wordpunct_tokenize
from nltk.stem.porter import PorterStemmer #Note: stem not stemmer - https://www.google.com.sg/search?q=NLTK+Porter+stemmer+import   #http://www.ibm.com/developerworks/library/l-cpnltk/index.html

import time

import getopt
import sys

class DictionaryTerm: #Token-DocID PairF
    def __init__(self, token, lastDocID=0, docFreq=1, docIDs=[]): #SYNT: make some parameters optional by providing default values
        self.token = token  #Should correspond with the key outside of this class
        self.lastDocID = lastDocID #for quicker checking for duplicate terms later during Merge+Split
        #self.freq  = freq
        self.docFreq = docFreq #the docFreq of unique docIDs
        #self.ptr   = ptr
        #self.lengthRead = lengthRead
        self.docIDs = [] #an empty array
    def printString(self):
        print str(self.token)+":\tlastID",str(self.lastDocID), ' freq',str(self.docFreq), str(self.docIDs)
    def toString_Dict(self, nextWritePositionPointer=0, lengthOfWrite=0): #Pure frequency not really needed for now
        return str(self.token)+ ' ' +str(self.docFreq)+ ' ' +str(nextWritePositionPointer)+ ' ' +str(lengthOfWrite)
    def toString_PLists(self):
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

def createSkips(docIDs):
    
    math.sqrt(len(docIDs))
    return 


debug=100
def collectTerms(dirPath, outFile_dictionary='dictionary.txt', outFile_postingsLists='postings.txt'):
#   if   debug==0: dirPath = '/home/course/cs3245/nltk_data/corpora/reuters/training/'
#    elif debug==2: dirPath = 'training/'
#    elif debug==1: dirPath = '/usr/local/lib/nltk_data/corpora/reuters/training/'
#    elif debug==4: dirPath = 'testGather/'
#    elif debug==6: dirPath = 'testLongGather/'
#    elif debug==100: dirPath = 'finalTraining/'
    startTime = time.time()
    fileList = os.listdir(dirPath)
    fileList = [x for x in fileList  if not (x.startswith('.'))] #Python ignore .DS_Store http://mail.python.org/pipermail/tutor/2004-April/029019.html
    #Ignore hidden files - http://stackoverflow.com/questions/7099290/how-to-ignore-hidden-files-using-os-listdir-python
    fileList = [int(x) for x in fileList] #Converting the elements to int, in order for sorted to work properly later.
    dictList = {}
    file_out_FullDocList = file("fullDocList.txt", 'w')
    #CONVERT HERE
    for eachInputFilename in sorted(fileList):
    #Ensure that fileList is sorted, so we can avoid sorting the postingsList docIDs later, where there will be a lot more to sort.
    #Need to ensure they are integers NOT strings during the sorting!! Else it will be 1,10,100,1000,..,2,20,..,3,..
        print >> file_out_FullDocList, str(eachInputFilename)
        docID = 0
        docID = eachInputFilename
        #docID, fileType = eachInputFilename.split('.', 1)  #for normal text files with extension
        print "opening file number " +str(docID)+ "..."
        eachDocPath = dirPath+ str(eachInputFilename)
        trainingData = open(eachDocPath, 'r')
        #if debug==1: print trainingData
        for eachLine in trainingData: #http://nltk.org/api/nltk.tokenize.html
            tokenizedSentences = sent_tokenize(eachLine)
            #if debug==1: print "Sentences", tokenizedSentences
            tokenizedWords = [word_tokenize(eachSentence) for eachSentence in tokenizedSentences]
            #if debug==1: print "Words:", tokenizedWords
            for eachTuple in tokenizedWords:
                for eachWord in eachTuple:
                    stemmedToken = PorterStemmer().stem_word(eachWord)
                    finalToken = stemmedToken.lower()
                    #if debug==3: print eachWord, eachWord.lower(), "| Stemmed:", stemmedToken

                    #Now there are 3 cases:
                    #(1) first occurence across all docs
                    #(2) first occurence within THIS doc
                    #(3) subsequent occurence within this doc
                    if finalToken not in dictList.keys(): #First occurence across all docs.
                        dictList[finalToken] = DictionaryTerm(finalToken,docID,1)
                        dictList[finalToken].docIDs.append(docID)
                        #This is creation. Frequency already "incremented" during creation.
                    elif docID != dictList[finalToken].lastDocID: #elif finalToken occurred in prev docs, hence alr in dictList.keys(), but current docID is bigger than lastDocID
                        if docID < dictList[finalToken].lastDocID: print "=====WARNING docs are not arranged in ascending int value!!====="
                        dictList[finalToken].docIDs.append(docID)
                        #dictList[finalToken].freq += 1
                        dictList[finalToken].docFreq += 1
                        dictList[finalToken].lastDocID = docID
                    elif docID == dictList[finalToken].lastDocID:
                        #Do not append since this is not new docID.
                        #dictList[finalToken].freq += 1 #ignore freq, just care about docFreq
                        pass
                        #No need to change the lastDocID since it remains same.
                    #if debug!=0: dictList[finalToken].printString()
    #end of ALL eachInputFilename in sorted(fileList)
    print "All files have been read and processed. Saving to Dictionary and Postings now."
#create_DP_Files(dictList, outFile_dictionary='dictionary.txt', outFile_postingsLists='postings.txt')  #write into the file
    file_outDictionary = file(outFile_dictionary, 'w')
    #file_outPostingsLists = file(outFile_postingsLists, 'r+') #r+ is for both reading n writing, file pointer at beginning of file
    file_outPostingsLists = file(outFile_postingsLists, 'w+') #w+ is for both writing n reading, will overwrite existing file. file pointer?
    finalToString = ""
    writeProgressCount = 0
    totalKeysCount = str(len(dictList.keys()))
    for eachToken in sorted(dictList.keys()):
        writeStartPosition = file_outPostingsLists.tell()
        print >> file_outPostingsLists, dictList[eachToken].toString_PLists()
        lengthOfWrite = file_outPostingsLists.tell() - writeStartPosition
        #print nextWritePosition
        print >> file_outDictionary, dictList[eachToken].toString_Dict(writeStartPosition, lengthOfWrite) #SYNTax: Cannot do a + string behind a string here. The plused part wont be written!!
        writeProgressCount += 1
        print "Progress : " +str(writeProgressCount)+'/'+totalKeysCount
    print "Total Time Elapsed:", time.time()-startTime
    #end of for eachToken
#end of function collectTerms()


#==================================================
def usage():
    print "usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file"

input_directory = outFile_dictionary = outFile_postingsLists = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-i':
        input_directory = a
    elif o == '-d':
        outFile_dictionary = a
    elif o == '-p':
        outFile_postingsLists = a
    else:
        assert False, "unhandled option"
if input_directory == None or outFile_dictionary == None or outFile_postingsLists == None:
    usage()
    sys.exit(2)
#==================================================
collectTerms(input_directory, outFile_dictionary, outFile_postingsLists)
#test_Dict_PLists('dictionary.txt', 'postings.txt')
#python testSyntax.py -i finalTraining/ -d finalDictionary.txt -p finalPostings.txt

