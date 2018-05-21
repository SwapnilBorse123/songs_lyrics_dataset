# AUTHOR: Swapnil Borse
# DATE: 05/19/2018
# REFERENCES: https://realpython.com/python-web-scraping-practical-introduction/

# I have picked few functions directly from the above mentioned reference website in order
# to avoid re-inventing the wheel.


from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import string, re
import inspect, os
from pathlib import Path

###############################################################################
# main function
###############################################################################
def main():
    songCounter = 0
    
    baseUrl = 'https://www.lyricsondemand.com'
    
    #links for scraping the given genres
    genresLinks = ['https://www.lyricsondemand.com/countrylyrics.html','https://www.lyricsondemand.com/christianlyrics.html','https://www.lyricsondemand.com/oldieslyrics.html','https://www.lyricsondemand.com/trendinglyrics.html','https://www.lyricsondemand.com/hiphoplyrics.html','https://www.lyricsondemand.com/rocklyrics.html']    
    
    for link in genresLinks:
        #link = genresLinks[0]
        cg = link.split('/')[3].replace('.html','')
        print('INFO: Scraping for genre: ' + link)
        genrePath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/' + cg + '/'
        
        #make a folder for current genre inside root folder
        if not os.path.exists(genrePath):
            os.makedirs(genrePath)
        
        for currChar in list(map(chr, range(ord('a'), ord('z')+1))):
            #currChar = 'a';
            print('INFO: Scraping for character: ' + currChar)
            charUrl = baseUrl + '/' + cg + '/' + currChar + '.html'
            charArtist = simple_get(charUrl)
            chrArtHtml = BeautifulSoup(charArtist, 'html.parser')
            spanArr = []
            try:
                spanArr = chrArtHtml.findAll('span',attrs={'class':'Highlight'})
            except:
                print("ERROR: No span elements found for artist. Probably missing elements!")
            print('LOG: spanArr len: ' + str(len(spanArr)))
            nameList = list()
            
            for i in range(0, len(spanArr)):
                nameList.append(spanArr[i].find('a').text.replace('Lyrics','').strip())
            print('Number of Names: ' + str(len(nameList)))
            
            for j in range(0, len(nameList)):
                #j = 0
                artistPath = genrePath + nameList[j].split('\n')[0]
                print('INFO: \n\n****** Current Artist: ' + nameList[j] + ' ******\n')
                if not os.path.exists(artistPath):
                    os.makedirs(artistPath)
                else:
                    print("INFO: Artist exists, skipping!")
                    continue
                artistUrl = baseUrl + '/' + currChar + '/' + nameList[j].replace(' ','').lower() + 'lyrics/index.html'
                artistPage = ''
                try:
                    artistPage = simple_get(artistUrl)
                except:
                    print('Error: Could not retrieve data for: ' + artistUrl)
                aSpanArr = []
                try:
                    songListPage = BeautifulSoup(artistPage, 'html.parser')
                    aSpanArr = songListPage.findAll('span',attrs={'class':'Highlight'})
                except:
                    print("ERROR: No span elements found. Probably missing elements!")
            
                for k in range(0, len(aSpanArr)):
                    fileName = ""
                    try:
                        #k = 0;
                        fileName = aSpanArr[k].find('a').text
                        if len(fileName) > 100:
                            fileName = fileName[:100]
                        print('INFO: Writing to file: ' + fileName)
                        filePath = artistPath + '/' + fileName
                        if os.path.isfile(filePath):
                            continue
                        lyricsUrl = artistUrl.replace('index.html', aSpanArr[k].find('a')['href'])
                        lyricsPage = simple_get(lyricsUrl)
                        lyricsHtml = BeautifulSoup(lyricsPage, 'html.parser')
                        lyric = ""
                        try:
                            lyric = lyricsHtml.find('div', attrs={'class':'lcontent'}).text.replace('<br/>','\n')
                            lyric = re.sub(r'\n{2,10}', '',lyric)
                        except:
                            print('ERROR: Empty Lyrics!')
                        try:
                            file = open(filePath, 'w')
                            file.write(lyric)
                            file.close()
                            songCounter += 1
                            if songCounter % 10 == 0:
                                print('INFO: Songs Crawled: ' + str(songCounter))
                        except IOError:
                            print('ERROR: Error with fileIO')
                    except:
                        print('ERROR: Empty Lyrics for URL: ' + lyricsUrl)
                    #print(inspect.getfile(inspect.currentframe())) # script filename (usually with path)
                    #print(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
                    
    print("INFO: Total songs crawled: " + str(songsCounter));


###############################################################################
# function to check if the response is ligit
###############################################################################
def is_good_response(resp):
    """
    Returns true if the response seems to be HTML, false otherwise
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


###############################################################################
#  function to log error
###############################################################################
def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)



###############################################################################
# function to return the data after a HTTP Request
###############################################################################
def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None
    

__init__ = main()