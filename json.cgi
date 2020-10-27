#!/home/bostonnp/virtualenv/public__html_tap/3.6/bin/python
print("Content-type: text/json")
print()
import cgi
import datetime
import json
import os
import subprocess
#uncomment next two lines for debug info
#import cgitb
#cgitb.enable()

#get arguments from URL, i.e. ?date=YYYY-MM-DD
postData = cgi.FieldStorage()

#default to today's date if no date argument supplied.
dateReq = datetime.date.today().isoformat()


#function to get nps events data from api using wget program.
#Essentially looks for the key in nps.key, uses date supplied as function argument,
#And makes that GET request, storing response as a file YYYY-MM-DD.json
#to do: if multi page, get each page and concatenate to one big json file.
def getNPS(d):
    key = open("nps.key")
    subprocess.run(["wget", "https://developer.nps.gov/api/v1/events?parkCode=bost%2Cboaf%2Cboha&dateStart=" + d + "&dateEnd=" + d +"&pageSize=50&pageNumber=1&expandRecurring=true&api_key=" + key.read(), "-O", d + ".json"])
    key.close()


#main request flow:

if "date" in postData:
    #if there is a date given as url argument, that is the date we are dealing with
	dateStrArray = postData['date'].value.split("-")
	dateReq = datetime.date(int(dateStrArray[0]),int(dateStrArray[1]),int(dateStrArray[2])).isoformat()

try:
    #file already exist?
    file = os.stat(dateReq + ".json")
    if datetime.datetime.timestamp(datetime.datetime.now()) - file.st_mtime > 86400:
        #if file is older than 24 hours, refresh it
        getNPS(dateReq)
except FileNotFoundError:
    #if this is first request for date given, get the data from nps.
    getNPS(dateReq)

#return final data with UTF-8 encoding
file = open(dateReq + ".json",encoding="utf-8")
DATA = json.loads(file.read())
file.close()
print(json.dumps(DATA))
