# -*- coding: utf-8 -*- 

import os
import sys
import xbmc
import struct
import urllib
import urllib2
import xbmcvfs
import xmlrpclib
import xbmcaddon
import unicodedata
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

__addon__      = xbmcaddon.Addon()
__version__    = __addon__.getAddonInfo('version') # Module version
__scriptname__ = "XBMC Subtitles"

class OSDBServer:
  def __init__( self, *args, **kwargs ):
    self.search_uri = 'http://subsunacs.net/search.php'
    self.opener = urllib2.build_opener(
      urllib2.HTTPRedirectHandler(),
	  urllib2.HTTPHandler(debuglevel=0),
	  urllib2.HTTPSHandler(debuglevel=0)
    )
    self.opener.addheaders = [
	  ('User-agent', ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6'))
	]

  def handleSearch(self, searchParams):

    #print ("handleSearch 1")
	# we always search for bg subs
    lang_name = 'Bulgarian'
    lang_code = 'bg'
    flag_image = "flags/%s.gif" % lang_code
    sync = False
    hear_imp = False
    subtitles = []

    try:
      soup = self._getSearchResultsSoup(searchParams)
      print ("got service response: %s" % soup)

      for detail in soup.findAll('a', {'class' : 'tooltip'}):
        name = detail.text.strip()
        cd = detail.findParent("td").findNextSibling('td')
        ratLink = cd.findNextSibling('td').findNextSibling('td').a
        rating = '0'
        
        print ('item name:%s cd:%s ratLink:%s' % (name, cd, ratLink))
        
        
        if ratLink and ratLink.img:
          rating = cd.findNextSibling('td').findNextSibling('td').a.img.get('alt')
                 
        if detail.get('href').startswith('http'):
          link = detail.get('href') 
        else: 
          link = ('http://subsunacs.net/%s' % detail.get('href'))
         
        print ('item rating:%s link:%s' % (rating, link))
        
        downloads = cd.findNextSibling('td').findNextSibling('td').findNextSibling('td').findNextSibling('td').findNextSibling('td')
        subtitles.append({'filename'      : ("DL:%s CD:%s - %s" % (downloads.text,
                                              cd.text,
                                              name)),
                                    'link'          : link,
                                    'language_name' : lang_name,
                                    'language_flag' : flag_image,
                                    'language_code'   : lang_code,
                                    'rating'        : rating,
                                    'format'        : 'rar'
                                   })
    except Exception, e:
      print("error: %s" % e)
      pass

    return subtitles

  def searchsubtitles(self, item):
    #print ("searchsubtitles 1")

    if item['mansearch']:
      searchParams = {'m' : urllib.unquote(item['mansearchstr']), 
	                            'l' : '0', 
								'c' : '', 
								'y' : '0', 
								'a' : '',
								'd' : '',
								'u' : '',
								'g' : '',
								't' : 'Submit'}
      print ("manual search: %s" % searchParams)
    elif len(item['tvshow']) > 0:
      searchParams = {'m' : ("%s %.2dx%.2d" % (item['tvshow'],
                                                int(item['season']),
                                                int(item['episode']))), 
								'l' : '0', 
								'c' : '', 
								'y' : '0', 
								'a' : '',
								'd' : '',
								'u' : '',
								'g' : '',
								't' : 'Submit'}
      print ("tvshow search: %s" % searchParams)
    else:
      if str(item['year']) == "":
        item['title'], item['year'] = xbmc.getCleanMovieTitle(item['title'])
	  
      if str(item['year']) == "":
        item['year'] = '0'

      searchParams = {'m' : item['title'], 
								'l' : '0', 
								'c' : '', 
								'y' : '0', 
								'a' : '',
								'd' : '',
								'u' : '',
								'g' : '',
								't' : 'Submit'}
      print ("title search: %s" % searchParams)

    log( __name__ , "Search Parameters [ %s ]" % (str(searchParams))) 

    result = self.handleSearch(searchParams)
    return result

  def download(self, link, dest):
      self.opener.addheaders = [
        ('User-agent', ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6')),
        ('Referer', link)
	    ]
      f = self.opener.open(link)
      with open(dest, "wb") as subArch:
        subArch.write(f.read())
      subArch.close()
      return True

  def _getSearchResultsSoup(self, searchParams, breakRec = False):
    
    data = urllib.urlencode(searchParams)
    f = self.opener.open(self.search_uri, data)
    soup = BeautifulStoneSoup(f.read())
    return soup


def log(module, msg):
  xbmc.log((u"### [%s] - %s" % (module,msg,)).encode('utf-8'),level=xbmc.LOGDEBUG ) 

def normalizeString(str):
  return unicodedata.normalize(
         'NFKD', unicode(unicode(str, 'utf-8'))
         ).encode('ascii','ignore')
