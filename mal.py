from bs4 import BeautifulSoup
import mechanize
import urllib2
import Queue
import sys
import time
import threading

requests = list()
class ThreadUrl(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
    def run(self):
        while True:
            #grabs host from queue
            host = self.queue.get()
    
            #grabs urls of hosts and prints first 1024 bytes of page
            url = urllib2.urlopen(host)
            requests.append(url.read())
            
            #signals to queue job is done
            self.queue.task_done()
            
def getUser():
    user = raw_input("Please input your MAL username: ")
    return user

def getArgs():
    if(len(sys.argv) > 1):
        if sys.argv[1] == '-s':
            return True
        
def getPage():
    br = mechanize.Browser()
    br.open("http://myanimelist.net/animelist/" + getUser())
    page = br.response()
    soup = BeautifulSoup(page,'html.parser')
    tables = soup.findAll("table")
    completeList = list()
    startAt = 0
    stopAt = 0
    count = 0
    for table in tables:
        found = table.find("div",{"class":"header_title"})
        count+=1
        if "Completed" in str(found):
            startAt = count + 1
            break
    counter = startAt
    while True:
        found = tables[counter].find("td", {"class":"category_totals"})
        if found != None:
            stopAt = counter
            break
        counter+=1
    for i in xrange(startAt,stopAt):
        completeList.append(tables[i])
    """for item in completeList:
        show = item.find("a",{"class":"animetitle"})
        name = show.find("span")
        name = str(name).replace("<span>","").replace("</span>","")
        #print name"""
    br.close()
    return completeList

def getUrls(shows):
    urlList = list()
    for item in shows:
        url = ""
        show = item.find("a",{"class":"animetitle"})
        url = u"http://myanimelist.net" + show.get('href')
        urlList.append(url.encode("utf-8"))
    return urlList

def openPage(url):
    response = urllib2.urlopen(url).read()
    soup = BeautifulSoup(response,'lxml')
    return soup

def TopenPage(url):
    soup = BeautifulSoup(url,'lxml')
    return soup

def searchRelated(soup,sequelsOnly):
    sequels = list()
    relatedTable = soup.find("table",{"class":"anime_detail_related_anime"})
    if relatedTable != None:
        if sequelsOnly:
            for tr in relatedTable.findAll("tr"):
                for anime in tr.findAll("a"):
                    if "Sequel:" in str(tr.find("td")) and anime.get_text() not in sequels:
                        sequels.append(anime.get_text())
        else:
            for tr in relatedTable.findAll("tr"):
                for anime in tr.findAll("a"):
                    if "Adaptation:" not in str(tr.find("td")) and anime.get_text() not in sequels:
                        sequels.append(anime.get_text())
    return sequels

def getRelated(urls,sequelsOnly):
    sequels = list()
    threads = []
    #for url in urls:
#        soup = openPage(url)
    for url in requests: 
        soup = TopenPage(url)
        relatedTable = soup.find("table",{"class":"anime_detail_related_anime"})
        if relatedTable != None:
            if sequelsOnly:
                for tr in relatedTable.findAll("tr"):
                    for anime in tr.findAll("a"):
                        if "Sequel:" in str(tr.find("td")) and anime.get_text() not in sequels:
                            sequels.append(anime.get_text())
            else:    
                for tr in relatedTable.findAll("tr"):
                    for anime in tr.findAll("a"):
                        if "Adaptation:" not in str(tr.find("td")) and anime.get_text() not in sequels:
                            sequels.append(anime.get_text())
    return sequels


                        
def unwatched(watched,related):
    unwatched = list()
    for item in related:
        if item not in watched:
            unwatched.append(item)
    return unwatched

def printShows(unwatched):
    unwatched.sort()
    number = 1
    for item in unwatched:
        print str(number) +" " + item
        number+=1        
        
        
starttime = time.time()        
sequelsOnly = getArgs()
shows = getPage()
names = list()
for show in shows:
    name = show.find("span")
    names.append(name.get_text())
urls = getUrls(shows)
queue = Queue.Queue()
for i in xrange(50):
    t = ThreadUrl(queue)
    t.setDaemon(True)
    t.start()
for url in urls:
    queue.put(url)
queue.join()

sequels = getRelated(urls,sequelsOnly)
unwatched = unwatched(names,sequels)
printShows(unwatched)
print "Total time: " + str(time.time()-starttime) +" seconds"
