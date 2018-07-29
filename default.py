import platform
import urllib2
import json
import sys
import re

# Replace with your file server IP Address
# Your file server host your movies and TV shows
networkShareIp = str('0.0.0.0')
shareName = 'movies'
payload = eg.event.payload[0]
print eg.event.payload[0].strip()

# Assigning a default player if no player is specified
print "Payload before: " + str(payload)
player = '0.0.0.0:8080'

# Stripping out player if player is specified
if re.search('in the bedroom', payload):
    player = '0.0.0.0:8080'
    payload = payload.replace(' in the bedroom', '')
if re.search('in the living room', payload):
    player = '0.0.0.0:8080'
    payload = payload.replace(' in the living room', '')
print "Payload after location striped out: " + str(payload)

# Stripping out put on when requesting TV channel
if re.search('put on', payload):
    payload = payload.replace('put on ', '')
    print "Payload after stripping out put on:" + str(payload)
    
breakdown = payload.split(' ',1)
command = breakdown[0];

payload = urllib2.quote(payload.replace(command, '').strip())

print "Payload after command striped out: " + str(payload)

print "Python Version: " + str(platform.python_version())
print "Phrase: " + str(eg.event.payload[0])
print "Player: " + str(player)
print "Breakdown: " + str(breakdown)
print "Command: " + str(command)

#TheMovieDB API Key; replace with your API key if you have one
apikey = ''

def getPlayerID ():
    url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"Player.GetActivePlayers","id":1}'
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    jsondata = json.loads(response.read())
    print jsondata
    playerID = jsondata['result'][0]['playerid']
    return playerID
    
def sendRequest(url):
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    jsondata = json.loads(response.read())
    print jsondata

def playTV(jsondata):
    tvShowTitle = urllib2.quote(jsondata['results'][0]['name'])
    print tvShowTitle
    
    # Displays TV show title
    try:
        url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"GUI.ShowNotification","params":{"title":"TV Shows","message":"' + tvShowTitle + '"},"id":1}'
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        jsondata = json.loads(response.read())
        print jsondata
    except Exception as e:
        print 'Error (Kodi MovieID): ', sys.exc_info()
        
    # Check to see if show is in Kodi
    try:
        url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"VideoLibrary.GetTVShows","params":{"filter":{"field":"title","operator":"is","value":"' + tvShowTitle + '"},"properties":["title"],"sort":{"order":"ascending","method":"label","ignorearticle":true}},"id":"libTvShows"}'
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        jsondata = json.loads(response.read())
        print jsondata
    except Exception as e:
        print sys.exc_info()
        
    # If it's in Kodi get the next unplayed episodeID then play
    if jsondata['result']['limits']['end'] <> 0:
        try:
            print 'Trying to play from Kodi'
            tvshowid = str(jsondata['result']['tvshows'][0]['tvshowid'])
            url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"VideoLibrary.GetEpisodes","params":{"filter":{"field":"playcount","operator":"is","value":"0"},"limits":{"end":1},"tvshowid":' + tvshowid + ',"properties":["season","episode","lastplayed","firstaired","resume","title","dateadded"],"sort":{"method":"episode","order":"ascending"}},"id":"libTvShows"}'
            print url
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            jsondata = json.loads(response.read())
            print jsondata
        except Exception as e:
            print sys.exc_info()
            
        if jsondata['result']['limits']['end'] == 0:
                try:
                    url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"GUI.ShowNotification","params":{"title":"TV Shows","message":"All episodes watched"},"id":1}'
                    req = urllib2.Request(url)
                    response = urllib2.urlopen(req)
                    jsondata = json.loads(response.read())
                    print jsondata
                except Exception as e:
                    print sys.exc_info()
        else:
            # Sending episodeid to player
            try:
                episodeid = str(jsondata['result']['episodes'][0]['episodeid'])
                url = 'http://' + player + '/jsonrpc?request={"id":1,"jsonrpc":"2.0","method":"Player.Open","params":{"item":{"episodeid":' + episodeid + '},"options":{"resume":true}}}'
                print url
                req = urllib2.Request(url)
                response = urllib2.urlopen(req)
                jsondata = json.loads(response.read())
                print jsondata
            except Exception as e:
                print sys.exc_info()
                
    # Streaming from Exodus
    else:
        print 'Streaming from Exodus'
        
        # Getting Trakt progress data
        try:
            print 'Trying to play from Exodus'
            url = 'http://' + player + '/jsonrpc?request={"id":1,"jsonrpc":"2.0","method": "Files.GetDirectory","params":{"directory":"plugin://plugin.video.exodus/?action=calendar%26url=progress"}}}'
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            jsondata = json.loads(response.read())
            print url
            print 'Shows in Trakt'
            print jsondata
        except Exception as e:
            print sys.exc_info()
        
        # Scanning for requested show in Trakt progress data
        traktInfo = None
        for files in jsondata['result']['files']:
            if re.search(urllib2.unquote(tvShowTitle), urllib2.unquote(files['file'].replace('+', ' '))):
                traktInfo = urllib2.quote(files['file'])
                # Using Trakt data to get information needed to stream show
                try:
                    url = 'http://' + player + '/jsonrpc?request={"id": 1, "jsonrpc": "2.0", "method": "Files.GetDirectory","params":{"directory":"' + traktInfo + '" } }'
                    req = urllib2.Request(url)
                    response = urllib2.urlopen(req)
                    jsondata = json.loads(response.read())
                    print jsondata
                    episodeInfo = urllib2.quote(jsondata['result']['files'][0]['file'])
                except Exception as e:
                    print sys.exc_info()
     
                # Sending episode information to player to start stream
                try:
                    url = 'http://' + player + '/jsonrpc?request={"id":1,"jsonrpc":"2.0","method":"Player.Open","params":{"item":{"file":"' + episodeInfo + '"},"options":{"resume":true}}}'
                    req = urllib2.Request(url)
                    response = urllib2.urlopen(req)
                    jsondata = json.loads(response.read())
                    print jsondata
                except Exception as e:
                    print sys.exc_info()

        if traktInfo == None:
            print 'Playing Season 1 Episode 1 of a new show'
            trakturl = 'http://api.trakt.tv/search/show?limit=1&page=1&query=' + tvShowTitle
            print trakturl
            try:
                url = 'http://' + player + '/jsonrpc?request={"id": 1, "jsonrpc": "2.0", "method": "Files.GetDirectory","params":{"directory":"plugin://plugin.video.exodus/?action=tvshowPage%26url=' + urllib2.quote(trakturl).replace("/","%2F").replace("%","%25") + '" } }'
                print url
                req = urllib2.Request(url)
                response = urllib2.urlopen(req)
                jsondata = json.loads(response.read())
                print jsondata
                print jsondata['result']['files'][0]['file']
                showInfo = urllib2.quote(jsondata['result']['files'][0]['file'].replace('action=seasons','action=episodes') + '&season=1')
                print showInfo
            except Exception as e:
                print 'Error (Trakt API): ', sys.exc_info()
        
            try:
                url = 'http://' + player + '/jsonrpc?request={"id": 1, "jsonrpc": "2.0", "method": "Files.GetDirectory","params":{"directory":"' + showInfo + '" } }'
                print url
                req = urllib2.Request(url)
                response = urllib2.urlopen(req)
                jsondata = json.loads(response.read())
                print jsondata
                episodeInfo = urllib2.quote(jsondata['result']['files'][0]['file'])
            except Exception as e:
                print sys.exc_info()

            try:
                url = 'http://' + player + '/jsonrpc?request={"id":1,"jsonrpc":"2.0","method":"Player.Open","params":{"item":{"file":"' + episodeInfo + '"},"options":{"resume":true}}}'
                print url
                req = urllib2.Request(url)
                response = urllib2.urlopen(req)
                jsondata = json.loads(response.read())
                print jsondata
            except Exception as e:
                print sys.exc_info()
            
def playMovie(jsondata):
    movieTitle = urllib2.quote(jsondata['results'][0]['title'])
    print 'The Movie Title', movieTitle
    
    # Displays movie title
    try:
        url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"GUI.ShowNotification","params":{"title":"Movies","message":"' + movieTitle + '"},"id":1}'
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        jsondata = json.loads(response.read())
        print jsondata
    except Exception as e:
        print 'Error (Kodi MovieID): ', sys.exc_info()
        
    try:
        url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"VideoLibrary.GetMovies","params":{"filter":{"field":"title","operator":"is","value":"' + movieTitle + '"},"properties":["title"],"sort":{"order":"ascending","method":"label","ignorearticle":true}},"id":"libMovies"}'
        print url
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        jsondata = json.loads(response.read())
        print jsondata
    except Exception as e:
        print 'Error (Kodi MovieID): ', sys.exc_info()
            
    if jsondata['result']['limits']['end'] == 0:
        print 'The movie is not in the library.'
        trakturl = 'http://api.trakt.tv/search/movie?limit=1&page=1&query=' + movieTitle
        print trakturl
        try:
            url = 'http://' + player + '/jsonrpc?request={"id": 1, "jsonrpc": "2.0", "method": "Files.GetDirectory","params":{"directory":"plugin://plugin.video.exodus/?action=moviePage%26url=' + urllib2.quote(trakturl).replace("/","%2F").replace("%","%25") + '" } }'
            print url
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            jsondata = json.loads(response.read())
            print jsondata
            print jsondata['result']['files'][0]['file']
            fileblob = urllib2.quote(jsondata['result']['files'][0]['file'])
        except Exception as e:
            print 'Error (Trakt API): ', sys.exc_info()
        try:
            url = 'http://' + player + '/jsonrpc?request={"id":1,"jsonrpc":"2.0","method":"Player.Open","params":{"item":{"file":"' + fileblob + '"},"options":{"resume":true}}}'
            print url
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            jsondata = json.loads(response.read())
            print jsondata
        except Exception as e:
            print sys.exc_info()
    else:
        movieid = str(jsondata['result']['movies'][0]['movieid'])
        print movieid
        try:
            url = 'http://' + player + '/jsonrpc?request={"id":1,"jsonrpc":"2.0","method":"Player.Open","params":{"item":{"movieid":' + movieid + '},"options":{"resume":true}}}'
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            jsondata = json.loads(response.read())
            print jsondata
        except Exception as e:
            print sys.exc_info()

def downloadMovie(payload):
    print 'Downloading'
    try:
        url = 'https://api.themoviedb.org/3/search/multi?include_adult=false&page=1&query=' + payload + '&language=en-US&api_key=' + apikey;
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        jsondata = json.loads(response.read())
        print jsondata
        print jsondata['total_results']
        if jsondata['total_results'] <> 0:
            print 'test'
            try:
                movieTitle = jsondata['results'][0]['title']
            except Exception as e:
                movieTitle = jsondata['results'][0]['name']
            tmdbId = jsondata['results'][0]['id']
            imagePath = 'https://image.tmdb.org/t/p/w640' + jsondata['results'][0]['poster_path']
            titleBlob = (movieTitle + ' ' + str(tmdbId)).replace(' ','-').lower();
            print movieTitle
            print tmdbId
            print imagePath
            print titleBlob
        else:
            print 'Movie doesn\'t exist'
            exit(0)
    except Exception as e:
        print 'Error themoviedb: ', sys.exc_info()

    try:
        data = '{"qualityProfileID":"4","monitored":"true","rootFolderPath":"\\\\\\\\' + networkShareIp + '\\\\' + shareName + '","title":"' + movieTitle + '","images":[{"covertype":"poster","url":"' + imagePath + '"}],"titleslug":"' + titleBlob + '","tmdbId":"' + str(tmdbId) + '"}'
        print data
        url = 'http://10.178.0.118:7878/api/movie'
        req = urllib2.Request(url)
        req.add_header('Content-Type','application/json')
        req.add_header('X-Api-Key', '')
        urllib2.urlopen(req,data)
    except Exception as e:
        print 'Error (Radarr): ', sys.exc_info()

if command == 'play' or command == 'watch' or command == 'played':
    print 'Playing'
    # Contacting theMovieDB for properly formated TV show or movie name
    # Exit if can't find name
    try:
        url = 'https://api.themoviedb.org/3/search/multi?include_adult=false&page=1&query=' + payload + '&language=en-US&api_key=' + apikey;
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        jsondata = json.loads(response.read())
        print jsondata
        print jsondata['total_results']
        if jsondata['total_results'] <> 0:
            mediatype = jsondata['results'][0]['media_type']
            print mediatype;
        else:
            print 'No TV Show or Movie with that name exist'
            exit(0)
    except Exception as e:
        print 'Error themoviedb: ', sys.exc_info()
        
    if mediatype == 'movie':
        playMovie(jsondata)
                
    if mediatype == 'tv':
        playTV(jsondata)
        
elif command == 'download':
    downloadMovie(payload)
    
elif command == 'scan':
    url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"VideoLibrary.Scan","id":1}'
    sendRequest(url)

elif command == 'exit':
    url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"Application.Quit","id":1}'
    sendRequest(url)
    
elif command == 'clean':
    url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"VideoLibrary.Clean","id":1}'
    sendRequest(url)
    
elif command == 'Exodus':
    url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"GUI.ActivateWindow","params":{"window":"videos","parameters":["plugin://plugin.video.exodus"]},"id":1}'
    sendRequest(url)

# Send request to tasker if running on Android TV
elif command == 'Hulu' or command == 'Amazon' or command == 'Netflix' or command == 'Plex' or command == 'Kodi' or command == 'radar' or command == 'deluge' or command == 'settings' or command == 'live' or command == 'Tasker':
    url = 'http://10.178.88.174:8765?launch=' + command
    print url
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    
elif command == 'home':
    url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"Input.Home","id":1}'
    sendRequest(url)

elif command == 'stop':
	playerID = str(getPlayerID())
	url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"Player.Stop","params":{ "playerid": ' + playerID + '},"id":1}'
	sendRequest(url)

elif command == 'pause' or command == 'resume' or command == 'Paws':
	playerID = str(getPlayerID())
	url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"Player.PlayPause","params":{"playerid":' + playerID + '},"id":1}'
	sendRequest(url)

elif command == 'context' or command == 'long':
	url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"Input.ContextMenu","id":1}'
	sendRequest(url)

elif command == 'select' or command == 'enter':
	url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"Input.Select","id":1}';
	sendRequest(url)

elif command == 'Sophie' or command == 'butt':
    url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"GUI.ShowNotification","params":{"title":"SophieGram","message":"You are a buttface!"},"id":1}'
    sendRequest(url)

elif command == 'TV':
    url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"GUI.ActivateWindow","id":1,"params":{"window":"tvguide"}}'
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    jsondata = json.loads(response.read())
    print jsondata

# Query Kodi for PVR channel labels and test if label matches request
else:
    try:
        url = 'http://' + player + '/jsonrpc?request={"jsonrpc": "2.0", "method": "PVR.GetChannels", "params": {"channelgroupid": "alltv", "properties" :["uniqueid"]},"id": 1}'
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        jsondata = json.loads(response.read())
        print jsondata
        print jsondata['result']
        for labels in jsondata['result']['channels']:
            print labels['label']
            if command.upper() == labels['label'].split(' ',1)[0].upper():
                url = 'http://' + player + '/jsonrpc?request={"id":1,"jsonrpc":"2.0","method":"Player.Open","params":{"item":{"channelid":' + str(labels['channelid']) + '}}}'
                req = urllib2.Request(url)
                response = urllib2.urlopen(req)
                jsondata = json.loads(response.read())
                print jsondata
                exit(0)
    except Exception as e:
        # print sys.exc_info()
        print 'Couldn\'t retreive channel list. Maybe Kodi is running?'
