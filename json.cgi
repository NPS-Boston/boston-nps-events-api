#!/home/bostonnp/virtualenv/public__html_tap/3.6/bin/python
print("Content-type: text/json")
print()
import cgi
import datetime
import json
import os
import subprocess
import math
#uncomment next two lines for debug info
#import cgitb
#cgitb.enable()

#get arguments from URL, i.e. ?date=YYYY-MM-DD
postData = cgi.FieldStorage()

#default to today's date if no date argument supplied.
dateReq = datetime.date.today().isoformat()
dateEnd = ""
#global vars for the json file and object/dict that will be/has been in existence for date requested.
file = ''
DATA = {}

#URI encoded list of park alpha codes to pull from api
parkCodes = "bost%2Cboaf%2Cboha"


#function to get nps events data from api using wget program.
#Essentially looks for the key in nps.key, uses date supplied as function argument,
#And makes that GET request, storing response as a file YYYY-MM-DD.json
#If response is multi-page (max page size appears to be 50), get every page and concat into one big json file.
def getNPS(d, de=""):
    kf = open("nps.key")
    key = kf.read()
    kf.close()
    fn = d + ".json"
    if de != "":
        fn = d + "_" + de + ".json"
    else:
        de = d
    subprocess.run(["wget", "https://developer.nps.gov/api/v1/events?parkCode=" + parkCodes + "&dateStart=" + d + "&dateEnd=" + de + "&pageSize=50&pageNumber=1&expandRecurring=true&api_key=" + key, "-O", fn])
    file = open(fn,encoding="utf-8")
    DATA = json.loads(file.read())
    if int(DATA["total"]) > int(DATA["pagesize"]):
        loops = math.ceil(int(DATA["total"]) / int(DATA["pagesize"]))
        for i in range(2,loops + 1):
            subprocess.run(["wget", "https://developer.nps.gov/api/v1/events?parkCode=" + parkCodes + "&dateStart=" + d + "&dateEnd=" + de +"&pageSize=50&pageNumber=" + str(i) + "&expandRecurring=true&api_key=" + key, "-O", "multipage." + str(i) + ".json"])
            tmp = open("multipage." + str(i) + ".json",encoding="utf-8")
            tmpDATA = json.loads(tmp.read())
            tmp.close()
            for j in tmpDATA["data"]:
                DATA["data"].append(j)
        DATA["pagesize"] = DATA["total"]
        file.close()
        file = open(fn,mode="w",encoding="utf-8")
        file.write(json.dumps(DATA))
    file.close()


#main request flow:

if "date" in postData:
    #if there is a date given as url argument, that is the date we are dealing with
	dateStrArray = postData['date'].value.split("-")
	dateReq = datetime.date(int(dateStrArray[0]),int(dateStrArray[1]),int(dateStrArray[2])).isoformat()
if "dateEnd" in postData:
    #if there is a date given as url argument, that is the date we are dealing with
	dateStrArray = postData['dateEnd'].value.split("-")
	dateEnd = datetime.date(int(dateStrArray[0]),int(dateStrArray[1]),int(dateStrArray[2])).isoformat()

try:
    #file already exist?
    if dateEnd == "":
        file = os.stat(dateReq + ".json")
    else:
        file = os.stat(dateReq + "_" + dateEnd + ".json")
    if datetime.datetime.timestamp(datetime.datetime.now()) - file.st_mtime > 86400:
        #if file is older than 24 hours, refresh it
        getNPS(dateReq, dateEnd)
except FileNotFoundError:
    #if this is first request for date given, get the data from nps.
    getNPS(dateReq, dateEnd)

#return final data with UTF-8 encoding
if dateEnd != "":
    file = open(dateReq + "_" + dateEnd + ".json",encoding="utf-8")
else:
    file = open(dateReq + ".json",encoding="utf-8")
DATA = json.loads(file.read())
file.close()
print(json.dumps(DATA))
