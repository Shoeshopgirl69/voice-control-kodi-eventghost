from __future__ import print_function
from http.server import HTTPServer, BaseHTTPRequestHandler
import time
import platform
import urllib.request
import json
import sys
import re

class Serv(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()  
        if "/Phrase?" in self.path:
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

    def phrase(self, text):
        #print(text)
        command = text.replace('%20',' ').lower().split(' ',1)[0]
        title = text.replace(command,'',1).strip()
        print(command)
        print(title)
        if command == 'download':
            self.downloadMovie(str(title))

        return

    def downloadMovie(self, title):
        try:
            print("Seeing if movie exists and sanitizing text")
            url = 'http://10.178.0.118:7878/api/movie/lookup?term=' + title.strip('%20') + '&apikey=4e1b73ddefa84185acfce6d261ed3790'
            req = urllib.request.Request(url)
            req.add_header('Content-Type','application/json')
            response = urllib.request.urlopen(req)
            jsondata = json.loads(response.read().decode('utf-8'))
            print(jsondata[0])
            if len(jsondata) != 0:
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
                    url = 'http://10.178.0.118:7878/api/movie?apikey=4e1b73ddefa84185acfce6d261ed3790'
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
                        data = '{"qualityProfileID":"4","monitored":"true","rootFolderPath":"\\\\\\\\10.178.100.1\\\\Movies","title":"' + movieTitle + '","images":[{"covertype":"poster","url":"' + imagePath + '"}],"titleslug":"' + titleBlob + '","tmdbId":"' + str(tmdbId) + '"}'
                        url = 'http://10.178.0.118:7878/api/movie?apikey=4e1b73ddefa84185acfce6d261ed3790'
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

httpd = HTTPServer(('10.178.0.118', 34567), Serv)
print(time.asctime(), "Server Starts - %s:%s" % ('localhost', '34567'))
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
	
httpd.server_close()
print(time.asctime(), "Server Stops - %s:%s" % ('localhost', '34567'))
