#ASGN3

#!/usr/bin/python
import os
import glob
import nltk
#from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tokenize import sent_tokenize, word_tokenize, wordpunct_tokenize
from nltk.stem.porter import PorterStemmer #Note: stem not stemmer - https://www.google.com.sg/search?q=NLTK+Porter+stemmer+import   #http://www.ibm.com/developerworks/library/l-cpnltk/index.html

import math

import time

import getopt
import sys



#zones and fields
# valuation and x
#architecture
#documentation

class Posting: #Replaces docIDs -- docID contained integer -- Posting has docID AND termFreq
    def __init__(self, docID, termFreq=1):
        self.docID = docID
        self.termFreq = termFreq #Num times term appears in A document for EACH document
        self.logFreqWeight = 0.0  #Calc in FINAL. Zero for now. MUST BE FLOAT!!
        self.TfxIdf = 0.0
    def calc_logFreqWeight(self):
        if self.termFreq>0: #To avoid ERROR due to Log(ZERO).
            self.logFreqWeight = 1.0+ math.log10(self.termFreq) #ALT: math.log10(self.termFreq) vs math.log(self.termFreq, 10)
        elif self.termFreq<=0:
            self.logFreqWeight = 0.0
        return self.logFreqWeight ##Change in code struct. Now using return value in calc_TfxIdf  ## Not really necessary since this function is called during indexing. During searching, the direct variable is used, and this function is NOT called.
    def calc_TfxIdf(self, invDocFreq_from_DictionaryTerm_class):
        self.TfxIdf = self.calc_logFreqWeight() * invDocFreq_from_DictionaryTerm_class #Both of them are CONFIRMED Floats already.
        #DONT need to calculate TfxIdf for documents in this assignment
        #return self.TfxIdf
    def toString_wHeaders(self):
        return "(id" +str(self.docID)+ ", tf" +str(self.termFreq)+ ", weight" +str(self.logFreqWeight)+"&"+str(self.TfxIdf)+ ")"
    def toString_forWrite(self):
        return str(self.docID)+ ":" +str(self.logFreqWeight) ##+ ":" +str(self.TfxIdf)   ##+ ":" +str(self.termFreq)
#end of the class


class DictionaryTerm: #Token-DocID PairF
    def __init__(self, token, lastDocID=0, docFreq=1, postings={}): #SYNT: make some parameters optional by providing default values
        self.token = token  #Should correspond with the key outside of this class
        self.lastDocID = lastDocID #for quicker checking for duplicate terms later during Merge+Split
        #---Freq Counts---
        self.docFreq = docFreq #Num docs that have this term - the docFreq of unique docIDs
        ###NOT USED.. self.collFreq = 1 #Num occurrences of term in collection, counts multiple occurrences
        self.invDocFreq = 0.0 #Calc in FINAL. Zero for now. MUST BE FLOAT!!
        #---Others---
        #self.ptr   = ptr
        #self.lengthRead = lengthRead
        #---Postings List---
        #self.docIDs = [] #an empty array
        self.postings = {} #empty array. array of Postings #Replaces docIDs -- docID contained integer -- Posting has docID AND termFreq
    def calcDerivatives(self, totalUniqueDocCount=7769): #7769 is Total Count of Reuters Documents in Folder
#        if totalUniqueDocCount != 7769: print "WARNING: Total Unique Doc Count is", totalUniqueDocCount, " and is NOT 7769!!"
        tmpInverse = 1.0*totalUniqueDocCount/self.docFreq
        self.invDocFreq = math.log10(tmpInverse) #ALT: math.log10(self.termFreq) vs math.log(self.termFreq, 10)
        if self.invDocFreq == 0:
            print "WARNING! invDocFreq 0 -- Check", "'"+self.token+"'", "==> docFreq", str(self.docFreq), "tmpInverse", tmpInverse
            print "WARNING! invDocFreq 0 -- Check", self.token, "==> docFreq", str(self.docFreq), "tmpInverse", tmpInverse
            print '\n'*5
        for eachPosKey in self.postings:
            self.postings[eachPosKey].calc_logFreqWeight() #But now we aren't doing .calc_TfxIdf()  #This is already done inside of .calc_TfxIdf()
            #self.postings[eachPosKey].calc_TfxIdf(self.invDocFreq)
    def printString(self):
        print str(self.token)+":\tlastID",str(self.lastDocID), ' freq',str(self.docFreq), toString_PListsRanked()

    def toString_Dict(self, nextWritePositionPointer=0, lengthOfWrite=0): #Pure frequency not really needed for now
        return str(self.token)+ ' ' +str(self.docFreq)+ ' ' +str(nextWritePositionPointer)+ ' ' +str(lengthOfWrite)
    def toString_DictRanked(self, nextWritePositionPointer=0, lengthOfWrite=0): #Pure frequency not really needed for now
        return str(self.token)+ ' ' +str(self.invDocFreq)+ ' ' +str(nextWritePositionPointer)+ ' ' +str(lengthOfWrite)

    def toString_PLists(self): #FOR BOOLEAN
        theToString = '' #Need to assign first before you can do += in the loop part. Else UnboundLocalError.
        #theToString += str(self.token) + ' '  #WARNING: only enable for debugging - to see if postings match dict
        for eachDocID in self.docIDs:
            theToString += str(eachDocID) + ' '
        return theToString
    def toString_PListsRanked(self): #For postings[] instead of docIDs[]
        theToString = '' #Need to assign first before you can do += in the loop part. Else UnboundLocalError.
        #theToString += str(self.token) + ' '  #WARNING: only enable for debugging - to see if postings match dict
        for eachPosKey in sorted(self.postings):
            theToString += self.postings[eachPosKey].toString_forWrite() + ' '
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
        tokenName, invDocFreq, pointer, lengthOfRead = eachDictLine.split(' ', 3)
        print "after split: " +tokenName, invDocFreq, pointer, lengthOfRead
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
    totalNumDocs = 0

    #CONVERT HERE
    for eachInputFilename in sorted(fileList):
    #Ensure that fileList is sorted, so we can avoid sorting the postingsList docIDs later, where there will be a lot more to sort.
    #Need to ensure they are integers NOT strings during the sorting!! Else it will be 1,10,100,1000,..,2,20,..,3,..
        print >> file_out_FullDocList, str(eachInputFilename)
        totalNumDocs += 1

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
                        dictList[finalToken].postings[docID] = Posting(docID,1)
                        #This is creation. Frequency already "incremented" during creation.
                    elif docID != dictList[finalToken].lastDocID: #elif finalToken occurred in prev docs, hence alr in dictList.keys(), but current docID is bigger than lastDocID
                        if docID < dictList[finalToken].lastDocID: print "=====WARNING docs are not arranged in ascending int value!!====="
                        dictList[finalToken].postings[docID] = Posting(docID,1)
                        dictList[finalToken].docFreq += 1
                        dictList[finalToken].lastDocID = docID
                    elif docID == dictList[finalToken].lastDocID:
                        #Do not append since this is not new docID.
                        dictList[finalToken].postings[docID].termFreq += 1  #array[-1] to access LAST element that was most recently appended
                        #pass
                        #No need to change the lastDocID since it remains same.
                    #if debug!=0: dictList[finalToken].printString()
        #Still in for-loop for eachInputFilename
        #CANNOT calculate the Derivative values for each term in THIS doc yet...
        #because need the total number of documents in this collection
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
        dictList[eachToken].calcDerivatives(totalNumDocs) #Calculates and stores logFreqWeight, invDocFreq, and TfxIdf. #totalNumDocs should be 7769
        writeStartPosition = file_outPostingsLists.tell()
        print >> file_outPostingsLists, dictList[eachToken].toString_PListsRanked()
        lengthOfWrite = file_outPostingsLists.tell() - writeStartPosition
        #print nextWritePosition
        print >> file_outDictionary, dictList[eachToken].toString_DictRanked(writeStartPosition, lengthOfWrite) #SYNTax: Cannot do a + string behind a string here. The plused part wont be written!!
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
#test_Dict_PLists('testDictionary.txt', 'testPostings.txt')
#python index.py -i trainingTMP/ -d testDictionary.txt -p testPostings.txt

