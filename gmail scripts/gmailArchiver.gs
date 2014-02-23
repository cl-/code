/* 
For use in Google Apps Script:
https://script.google.com/

Google Apps - Script - https://developers.google.com/apps-script/
GmailApp class - https://developers.google.com/apps-script/reference/gmail/

*/

var configurations = {
  trash: {
    delayDays: 7, // Enter # of days before messages are moved to TRASH
  },
  
  archive: {//Settings for mail to archive.
    delayDays: 60, // Enter # of days before messages are moved to Archive
    searchTerm: '',
    labels: [],
    labelsAnd: [],
    labelsExcluded: [],
    other: 0
  },

  //Configuration Settings for Gmail to <do something else>
  doSomethingElse: {}
};//endof configurations

function GmailArchiver(config){
  trashMail(config.trash.delayDays);

  archiveSearchTerm = createSearchTerm(config.archive);
  archiveInbox(archiveSearchTerm, config.delayDays);
};


function createSearchTerm(configObj){
  //Singular configObj for now.
  var searchTerm = 'label:(';
  for (var i=0; i<configObj.labels.length; ++i){
    searchTerm += ' OR"'+configObj.labels[i]+'"';}

  for (var i=0; i<configObj.labelsAnd.length; ++i){
    searchTerm += ' OR(';
    for(var j=0; j<configObj.labelsAnd[i].length; ++j){
      searchTerm += ' AND"'+configObj.labelsAnd[i][j]+'"';
    }
    searchTerm += ')';
  }
  searchTerm += ')';

  searchTerm += ' -label:(';
  for (var i=0; i<configObj.labelsExcluded.length; ++i)
    { searchTerm += ' OR"'+configObj.labelsExcluded[i]+'"'; }
  searchTerm += ')';

  return searchTerm;
}//endof createSearchTerm


function trashMail(delayDays){
  var maxDate = new Date();
  maxDate.setDate(maxDate.getDate()-delayDays);

  var label = GmailApp.getUserLabelByName("toTrash");
  var threads = label.getThreads();
  for (var i = 0; i < threads.length; i++) {
    if (threads[i].getLastMessageDate()<maxDate){
      threads[i].moveToTrash();
    }
  }
}//endof function trashMail

function archiveInbox(searchTerm, delayDays) {
  // // Every thread in your Inbox that is read, older than two days, and not labeled "delete me".
  // var threads = GmailApp.search('label:inbox is:read older_than:2d -label:"delete me"');
  var threads = GmailApp.search('older_than:'+delayDays+'d  label:inbox OR '+searchTerm);
  for (var i = 0; i < threads.length; i++) {
    threads[i].moveToArchive();
  }
}//endof function archiveInbox


/*
=========================
Allow script to access Gmail: http://www.johneday.com/422/time-based-gmail-filters-with-google-apps-script

Google Apps - Script - https://developers.google.com/apps-script/
GmailApp class - https://developers.google.com/apps-script/reference/gmail/

DIFFERENT FROM:
Google Apps Email Settings API - https://developers.google.com/admin-sdk/email-settings/
DIFFERENT FROM:
Gmail APIs - https://developers.google.com/gmail/

*/
