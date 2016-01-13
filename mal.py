from bs4 import BeautifulSoup
import mechanize
import urllib2


def getPage():
    br = mechanize.Browser()
    br.open("http://myanimelist.net/animelist/colecf")
    page = br.response()
    soup = BeautifulSoup(page,'html.parser')
    tables = soup.findAll("table")
    completeList = list()
    count = 0
    startAt = 0
    stopAt = 0
    for table in tables:
        found = table.find("div",{"class":"header_title"})
        count = count +1
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
    soup = BeautifulSoup(response)
    return soup

def unwatched(watched,related):
    unwatched = list()
    for item in related:
        if item not in watched:
            unwatched.append(item)
    for item in unwatched:
        print item
   

shows = getPage()
names = list()
for show in shows:
    name = show.find("span")
    names.append(name.get_text())
urls = getUrls(shows)
sequels = list()
for url in urls:
    soup = openPage(url)
    print url
    relatedTable = soup.find("table",{"class":"anime_detail_related_anime"})
    for tr in relatedTable.findAll("tr"):
        for anime in tr.findAll("a"):
            if "Adaptation:" not in str(tr.find("td")) and anime.get_text() not in sequels:
                sequels.append(anime.get_text())
#for show in sequels:
    #print show
#for name in names:
    #print name

unwatched(names,sequels)
