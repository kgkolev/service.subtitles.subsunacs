# -*- coding: utf-8 -*-

import os
import shutil
import sys
import urllib
import xbmc
import xbmcaddon
import xbmcgui,xbmcplugin
import xbmcvfs
import uuid
import re

__addon__ = xbmcaddon.Addon()
__author__     = __addon__.getAddonInfo('author')
__scriptid__   = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__    = __addon__.getAddonInfo('version')
__language__   = __addon__.getLocalizedString

__cwd__        = xbmc.translatePath( __addon__.getAddonInfo('path') ).decode("utf-8")
__profile__    = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) ).decode("utf-8")
__temp__       = xbmc.translatePath( os.path.join( __profile__, 'temp') ).decode("utf-8")

if xbmcvfs.exists(__temp__):
  shutil.rmtree(__temp__)
xbmcvfs.mkdirs(__temp__)

sys.path.append (__resource__)

from OSUtilities import OSDBServer, log, normalizeString

def Search( item ):
  search_data = []
  #print ("in Search method")
  try:
    search_data = OSDBServer().searchsubtitles(item)
  except:
    #print( __name__, "failed to connect to service for subtitle search")
    xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__ , __language__(32001))).encode('utf-8'))
    return

  #print(("done searching: %s" % search_data))
  if search_data != None:
    for item_data in search_data:
      listitem = xbmcgui.ListItem(label          = item_data["language_name"],
                                  label2         = item_data["filename"],
                                  iconImage      = str(int(round(float(item_data["rating"])))),
                                  thumbnailImage = item_data["language_code"]
                                  )

      listitem.setProperty( "sync", 'false')
      listitem.setProperty( "hearing_imp", 'false' )
      url = "plugin://%s/?action=download&link=%s&format=%s" % (__scriptid__,
                                                                        item_data["link"],
                                                                        item_data["format"])

      xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=False)


def Download(url,format,stack=False):
  subtitle_list = []
  exts = [".srt", ".sub", ".smi", ".ssa", ".ass" ]

  destDir = os.path.join(__temp__, str(uuid.uuid4()))
  xbmcvfs.mkdirs(destDir)
  dest = os.path.join(destDir, "%s.%s" % ('subtitles', format))
  OSDBServer().download(url, dest)

  xbmc.sleep(500)
  xbmc.executebuiltin(('XBMC.Extract("%s","%s")' % (dest,destDir)).encode('utf-8'), True)
  for file in xbmcvfs.listdir(dest)[1]:
    #print ("file: %s" % file)
    if (os.path.splitext(file)[1] in exts):
      file = os.path.join(destDir, file)
      subtitle_list.append(file)

  #print ("subtitle_list [ %s ]" % (str(subtitle_list))) 
  if len(subtitle_list) and xbmcvfs.exists(subtitle_list[0]):
    return subtitle_list

def get_params(string=""):
  param=[]
  if string == "":
    paramstring=sys.argv[2]
  else:
    paramstring=string
  if len(paramstring)>=2:
    params=paramstring
    cleanedparams=params.replace('?','')
    if (params[len(params)-1]=='/'):
      params=params[0:len(params)-2]
    pairsofparams=cleanedparams.split('&')
    param={}
    for i in range(len(pairsofparams)):
      splitparams={}
      splitparams=pairsofparams[i].split('=')
      if (len(splitparams))==2:
        param[splitparams[0]]=splitparams[1]

  return param

params = get_params()

if params['action'] == 'search' or params['action'] == 'manualsearch':
  log( __name__, "action '%s' called" % params['action'])
  item = {}
  item['temp']               = False
  item['rar']                = False
  item['mansearch']          = False
  item['year']               = xbmc.getInfoLabel("VideoPlayer.Year")                         # Year
  item['season']             = str(xbmc.getInfoLabel("VideoPlayer.Season"))                  # Season
  item['episode']            = str(xbmc.getInfoLabel("VideoPlayer.Episode"))                 # Episode
  item['tvshow']             = normalizeString(xbmc.getInfoLabel("VideoPlayer.TVshowtitle"))  # Show
  item['title']              = normalizeString(xbmc.getInfoLabel("VideoPlayer.OriginalTitle"))# try to get original title
  item['file_original_path'] = urllib.unquote(xbmc.Player().getPlayingFile().decode('utf-8'))# Full path of a playing file
  item['3let_language']      = [] #['scc','eng']
  PreferredSub		      = params.get('preferredlanguage')

  if 'searchstring' in params:
    item['mansearch'] = True
    item['mansearchstr'] = params['searchstring']

  for lang in urllib.unquote(params['languages']).decode('utf-8').split(","):
    if lang == "Portuguese (Brazil)":
      lan = "pob"
    else:
      lan = xbmc.convertLanguage(lang,xbmc.ISO_639_2)
      if lan == "gre":
        lan = "ell"

    item['3let_language'].append(lan)

  if item['title'] == "":
    log( __name__, "VideoPlayer.OriginalTitle not found")
    item['title']  = normalizeString(xbmc.getInfoLabel("VideoPlayer.Title"))      # no original title, get just Title

  if item['episode'].lower().find("s") > -1:                                      # Check if season is "Special"
    item['season'] = "0"                                                          #
    item['episode'] = item['episode'][-1:]
	
  if len(item['tvshow']) == 0:
    match = re.search("^(.*?)(?:[Ss](\d{1,2})[Ee](\d{1,2})|(\d{1,2})[Xx](\d{1,2})).*$", item['title'])
    if match:
      ttl, yr = xbmc.getCleanMovieTitle(item['title'])
      mttl = match.group(1).replace('.',' ').strip()
      item['tvshow'] = mttl if len(ttl) > len(mttl) else ttl
      #print ("%s %s %s %s" % (match.group(2), match.group(3), match.group(4), match.group(5)))
      item['season'] = int(match.group(4) if match.group(4) else match.group(2))
      item['episode'] = int(match.group(5) if match.group(5) else match.group(3))

  if ( item['file_original_path'].find("http") > -1 ):
    item['temp'] = True

  elif ( item['file_original_path'].find("rar://") > -1 ):
    item['rar']  = True
    item['file_original_path'] = os.path.dirname(item['file_original_path'][6:])

  elif ( item['file_original_path'].find("stack://") > -1 ):
    stackPath = item['file_original_path'].split(" , ")
    item['file_original_path'] = stackPath[0][8:]

  #print(("searching %s" % item))
  Search(item)

elif params['action'] == 'download':
  subs = Download(params["link"],params["format"])
  for sub in subs:
    listitem = xbmcgui.ListItem(label=sub)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=sub,listitem=listitem,isFolder=False)


xbmcplugin.endOfDirectory(int(sys.argv[1]))
