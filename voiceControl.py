from __future__ import print_function
from http.server import HTTPServer, BaseHTTPRequestHandler
import time
import platform
import urllib.request
import json
import sys
import re

serverIP = 'Replace' # IP of machine running this script
portNumber = 'Replace' # Port number this script should open
apikey = 'Replace' # Radarr API key
RadarrIP = 'Replace:Replace' # Radarr IP and port number
mediaPath = '\\\\\\\\Replace\\\\Movies' # Path supplied to Radarr to move movie
player = 'Replace:Replace' # Kodi IP and port number

class Serv(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()  
        if "/Phrase?" in self.path:
            print("Client IP Address: " + str(self.client_address[0]) + ":" + str(self.client_address[1]))
            preurl, text = self.path.split("?")
            # print("This is what I received: " + text)
            redir = "<html><head><title>Voice Control</title></head><body><h1>Message Received: "+text+"</h1></body></html>"
            # print(redir)
            self.wfile.write(redir.encode())
            self.phrase(str(text))
            return
            
        else:
            print("Yep, it's working")
            self.wfile.write("<html><head><title>Voice Control</title></head><body><h1>These aren't the droids you are looking for.</h1></body></html>".encode())
            return
   
    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        print( "incomming post: ", self.path )
        self._set_headers()
        self.wfile.write("<html><body><h1>I don't POST on the first date.</h1></body></html>".encode())

    def getPlayerID(self):
        url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"Player.GetActivePlayers","id":1}'
        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req)
        jsondata = json.loads(response.read())
        print(jsondata)
        playerID = jsondata['result'][0]['playerid']
        return playerID

    def phrase(self, text):
        #print(text)
        command = text.replace('%20',' ').lower().split(' ',1)[0]
        title = text.replace(command,'',1).strip()
        print(command)
        print(title)
        if command == 'download':
            self.downloadMovie(str(title))
        elif command == 'play':
            self.playMovie(str(title))
        elif command == 'scan':
            url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"VideoLibrary.Scan","id":1}'
            req = urllib.request.Request(url)
            response = urllib.request.urlopen(req)
        elif command == 'clean':
            url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"VideoLibrary.Clean","id":1}'
            req = urllib.request.Request(url)
            response = urllib.request.urlopen(req)
        elif command == 'exit':
            url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"Application.Quit","id":1}'
            req = urllib.request.Request(url)
            response = urllib.request.urlopen(req)
        elif command == 'pause' or command == 'resume' or command == 'Paws':
            playerID = str(self.getPlayerID())
            url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"Player.PlayPause","params":{"playerid":' + playerID + '},"id":1}'
            req = urllib.request.Request(url)
            response = urllib.request.urlopen(req)
        elif command == 'stop':
            playerID = str(self.getPlayerID())
            url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"Player.Stop","params":{ "playerid": ' + playerID + '},"id":1}'
            req = urllib.request.Request(url)
            response = urllib.request.urlopen(req)
        else:
            print("Whacha' talking about Willis")

        return

    def downloadMovie(self, title):
        try:
            print("Seeing if movie exists and sanitizing text")
            print(title)
            url = 'http://' + RadarrIP + '/api/movie/lookup?term=' + title + '&apikey=' + apikey
            print(url)
            req = urllib.request.Request(url)
            req.add_header('Content-Type','application/json')
            response = urllib.request.urlopen(req)
            jsondata = json.loads(response.read().decode('utf-8'))
            
            if len(jsondata) != 0:
                print(jsondata[0])
                print(jsondata[0]['title'])
                movieTitle = jsondata[0]['title']
                print(movieTitle)
                imagePath = jsondata[0]['images'][0]['url']
                print(imagePath)
                tmdbId = jsondata[0]['tmdbId']
                print(tmdbId)
                titleBlob = (movieTitle + ' ' + str(tmdbId)).replace(' ','-').lower()
                print(titleBlob)
                try:
                    # Get current Radarr data
                    entryExist = bool(0)
                    print("Looking to see if the movie is already in Radarr")
                    url = 'http://' + RadarrIP + '/api/movie?apikey=' + apikey
                    req = urllib.request.Request(url)
                    req.add_header('Content-Type','application/json')
                    response = urllib.request.urlopen(req)
                    jsondata = json.loads(response.read().decode('utf-8'))
                    print(time.asctime())
                    for titles in jsondata:
                        if movieTitle == titles['title']:
                            entryExist = bool(1)
                            print('Movie is already in Radarr')

                    if not entryExist:
                        data = '{"qualityProfileID":"4","monitored":"true","rootFolderPath":"' + mediaPath + '","title":"' + movieTitle + '","images":[{"covertype":"poster","url":"' + imagePath + '"}],"titleslug":"' + titleBlob + '","tmdbId":"' + str(tmdbId) + '"}'
                        url = 'http://' + RadarrIP + '/api/movie?apikey=' + apikey
                        params = bytes(data.encode())
                        req = urllib.request.Request(url)
                        req.add_header('Content-Type','application/json')
                        response = urllib.request.urlopen(req,params)
                        print("Okay, " + movieTitle + " has been added to Radarr")
                        # print(response.read().decode('utf-8'))
                        
                    print(time.asctime())
                        
                except Exception as e:
                    print('Error (Radarr): ', sys.exc_info())
            else:
                print('Movie doesn\'t exist')
            
        except Exception as e:
            print('Error themoviedb: ', sys.exc_info())

        return

    def playMovie(self, title):
        try:
            print("Seeing if movie exists and sanitizing text")
            url = 'http://' + RadarrIP + '/api/movie/lookup?term=' + title + '&apikey=' + apikey
            print(url)
            req = urllib.request.Request(url)
            req.add_header('Content-Type','application/json')
            response = urllib.request.urlopen(req)
            jsondata = json.loads(response.read().decode('utf-8'))
            print(jsondata[0])
            if len(jsondata) != 0:
                print(jsondata[0]['title'])
                movieTitle = jsondata[0]['title']                
                print('We are trying to play ', movieTitle)
                
                # Displays movie title
                try:
                    url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"GUI.ShowNotification","params":{"title":"Movies","message":"' + movieTitle + '"},"id":1}'
                    req = urllib.request.Request(url)
                    response = urllib.request.urlopen(req)
                    jsondata = json.loads(response.read())
                    print(jsondata)
                except Exception as e:
                    print('Error (Kodi MovieID): ', sys.exc_info())
                    
                try:
                    url = 'http://' + player + '/jsonrpc?request={"jsonrpc":"2.0","method":"VideoLibrary.GetMovies","params":{"filter":{"field":"title","operator":"is","value":"' + movieTitle + '"},"properties":["title"],"sort":{"order":"ascending","method":"label","ignorearticle":true}},"id":"libMovies"}'
                    print(url)
                    req = urllib.request.Request(url)
                    response = urllib.request.urlopen(req)
                    jsondata = json.loads(response.read())
                    print(jsondata)
                except Exception as e:
                    print('Error (Kodi MovieID): ', sys.exc_info())

                movieid = str(jsondata['result']['movies'][0]['movieid'])
                print(movieid)
                
                try:
                    url = 'http://' + player + '/jsonrpc?request={"id":1,"jsonrpc":"2.0","method":"Player.Open","params":{"item":{"movieid":' + movieid + '},"options":{"resume":true}}}'
                    req = urllib.request.Request(url)
                    response = urllib.request.urlopen(req)
                    jsondata = json.loads(response.read())
                    print(jsondata)
                except Exception as e:
                    print(sys.exc_info())

            else:
                print('Movie doesn\'t exist')
                          
        except Exception as e:
            print('Error themoviedb: ', sys.exc_info())
                    
        return

httpd = HTTPServer((serverIP, 34567), Serv)
print(time.asctime(), "Server Starts - %s:%s" % ('localhost', portNumber))
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
	
httpd.server_close()
print(time.asctime(), "Server Stops - %s:%s" % ('localhost', portNumber))
