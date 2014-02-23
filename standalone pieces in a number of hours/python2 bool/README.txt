== General Notes about this assignment ==

For my architecture, I created two classes to store the terms. A DictionaryTerm and the QueryTerm.

In index.py:
The DictionaryTerm allows me to be able to quickly retrieve the relevant values with the call of its properties. It also gives me a proper container to store the values neatly.

In general, my program works on the collectTerms function, which took about 60 to 70 lines after taking away the comments.

One special part about my collectTerms() function is that I performed sorting earlier on, to avoid wasting time sorting later on when there is a mess of term-docID pairs. I achieved this by converting the docID into integer from the start.

This helps save time to a rough factor that is times the number of terms present, since you have to sort for each dictionary term if the old method was used, whereas in my method, sorting only occurs of docID once.

In search.py:
I created lighter weight classes like DictionaryTermSmall, a lightweight version of DictionaryTerm to minimize the time taken to create the object. The same goes for QueryTerm and an even lighter weight ResolvedQueryTerm, which will be talked about in more detail further below.

I have mainly modularized the code into 4 parts:
1. the classes
2. the merge functions
3. the interior analyzer
4. the main startAnalysis function which is also handles bracketing issues

The bottom part, calls the part above it (eg 4 calls 3, which calls 2).

Did the tokenizing and stemming as per normal for each term, except that I skip the BOOLEAN terms [(,),NOT,AND,OR].

In the main function, brackets are processed while they still exist. When a bracket is processed, we look at the outer bracers, and then call the interior analyzer for its internal parts. Then internal analyzer processes NOT while NOT still exists, followed AND and then OR.

How this works is a List of QueryTerms are passed on. For the interior analysis, a selection of the list of QueryTerms are passed on - those List elements within the bracers. Then depending on whether it is a NOT, AND or OR, the corresponding merge is called.

During the processing and resolution of each BOOLEAN, a ResolutionTerm is returned. It is highly similar to a QueryTerm except that it has no real token. However, it can be used with the QueryTerm because they are like clones of each other, but ResolutionTerm is even lighter weight.

This ResolutionTerm replaces the resolved terms. ie The resolved terms are deleted from the List until there is only one element left in the list.

The interesting thing about interior analysis is that it can be easily reapplied to any interior portion of brackets. In addition, once there are no more brackets, it can be applied to the remaining terms. It is highly reusable.

I also created a test_Dict_PLists function that allows me to check the dictionary and postingslists easily.


== Files included with this submission ==

README.txt			- The readme

index.py
search.py

dictionary.txt
postings.txt
fullDocList.txt
