== General Notes about this assignment ==

Place your comments or requests here for Min to read.  Discuss your
architecture or experiments in general.  A paragraph or two is usually
sufficient.

-----
For my architecture, I created two classes to store the terms. A DictionaryTerm, the QueryTerm, the Posting and the docMatchResult.

In index.py:
The DictionaryTerm allows me to be able to quickly retrieve the relevant values with the call of its properties. It also gives me a proper container to store the values neatly.

In general, my program works on the collectTerms function, which took about 60 to 70 lines after taking away the comments.

One special part about my collectTerms() function is that I performed sorting earlier on, to avoid wasting time sorting later on when there is a mess of term-docID pairs. I achieved this by converting the docID into integer from the start.

This helps save time to a rough factor that is times the number of terms present, since you have to sort for each dictionary term if the old method was used, whereas in my method, sorting only occurs of docID once.

Math Functions:
I chose to use the math.log10() function instead of the math.log function because the documentation for python said that the log10() function would be more accurate. Hence, my results may differ from yours.

In search.py:
I created lighter weight classes like DictionaryTermSmall, a lightweight version of DictionaryTerm to minimize the time taken to create the object. The same goes for QueryTerm, PostingSmall and docMatchResult.

I have mainly modularized the code into 2 parts:
1. the classes
2. the main startAnalysis function

The bottom part, calls the part above it (eg 2 calls 1).

Did the tokenizing and stemming as per normal for each term.

In the main function, you first get the list of dicts form the dictionary.txt. Then you look at the queries and only retrieve their postingsList.

Now we need to treat the Query as a document and count the number of occurrences of the terms in that query document.

At the same time, check the dict and postingsList to find the list of docs that this term is associated with. This way, we can find the list of ALL documents that we need to check later for the lengthNormalization. The list of docs is stored as docMatchResult objects.

So we do the normalization for the Query doc first.
Then we repeat the process for Each Doc, for each query. That is why I created a new list of docMatchResults so that it is easier to see and understand the code.

Down here, I have optimized by skipping a step for zero values.
If the document has a 0.0 length, then I assign the addnlScore as 0.0, without doing any multiplication which is done for other documents with normal lengths:
addnlScore = queTokens[eachKey].lengthNormalization * normalizedLength_fromDoc

At the end, the sorting of the results is done with an algorithm that minimizes time taken. There is no separate 2nd or 3rd repeated for-loop to do the sorting. The sorting is all done within the first iteration of the loop, at the same time as we gather the document IDs.

Time is also saved because the sorting is done in mini-arrays - only the set of values for which the relevance is the same.

I also created a test_Dict_PLists function in the index.py that allows me to check the dictionary and postingslists easily. 

-----
I spent a few hours trying to debug the code, finally realizing that it was a default value of the constructor of the PostingSmall at fault. The default value in the index.py was 0.0 and I copy-transferred it over to search.py without changing it. However, in search.py, the default value was the value obtained from the postings list file, not 0.0. However, I did not notice that and spent a few hours wondering what was wrong.


For my experiments, I mainly tested out the syntax of Python.

Using a small sample sentence, I also tested out the data structures that I created to see if they worked to give the probabilities.
The result was that they gave the correct probabilities.

My experiments are mostly contained the testSyntax.py and the testSyntax folder.
Each test is separated by a line of "-" dashes and previous tests are commented in individual sections.
To try out each test, you can copy the commented section into the uncommented area to see how my tests run.

Thank you.


== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

README.txt			- The readme
ESSAY.txt			- The answers of my essay questions

index.py
search.py

dictionary.txt
postings.txt
fullDocList.txt

testSynt.py			- The things that I tried out. It is meant to be run as a standalone.


== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>

Googled to learn how to use the NLTK module
https://groups.google.com/forum/?fromgroups=#!forum/nltk-users

I consulted a friend with regards to Python syntax, on list returns.