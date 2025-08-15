

Business Problem: 

Google Drive constantly fills up with photos, email attachment and other large objects. Google appears to take customer's data hostage because they don't make it easy and simple to select the biggest data files to make space or download. There is no automated way to download files to a safe offline backup location.

requirements:
Ability to manage the download of google drive backups to a local, offline storate device
good security 
backup selection
 destination selection, download status, account and file type selection by file, size, date, error handling

 implementation: google drive services, API key, OAuth2, streamlit front end , complete logging to a time stamp file for every run. 


 This is just a starting point. Give me the following SDLC documentation; 
0. Revised project decription document.
 1.A good comprehensive Product Requirements Document(PRD) for the above draft requirements. Give me a beautifully formatted human readable PRD with every requirement uniquely defined.
 2. High level design document
 3. Low level design document
 
 Make sure all documents are indentified with a version number.

 Create a utility with Streamlit interface to manage Google Drive the process




*******************************************************

To make it easier for me to answer your clarifying questions, write out a nicely formatted file with placeholder for each one of the answers. Do not ask me mult-part questions, if possible make all question with yes or not answers.


## Suggested Next Small Enhancements (Low Risk)
- Wire mime/date filters into `list_files_generator`.
- Add Streamlit `st.progress` per file while downloading.
- Append `downloadedAt` and local path to manifest entries.
- Add simple test harness for `list_files_generator` with a mocked service.
- Provide `scripts/schedule_example_windows.bat` (if scheduling is in near scope).

## Your Clarifications Requested (Reply with answers)
Please respond with:
1. Implement date & mime filters now? (Y/N)
2. Add progress bars in UI? (Y/N)
3. Promote free-space check to MVP? (Y/N)
4. Add local SHA256 hashing? (Y/N)
5. Provide Windows scheduling example now? (Y/N)
6. Preferred license?
7. Target Python version(s)?
8. Multi-account / Shared Drive picker needed in MVP? (Y/N)
9. Encryption option in MVP? (Y/N)
10. Any branding/name change desired before finalizing docs?

Respond with a simple numbered list so I can proceed.

Let me know and I’ll implement the selected items next.