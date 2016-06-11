from __future__ import print_function
import time
import requests
import os
import re
from jinja2 import Template

import urllib

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi



# Variables

_url = 'https://api.projectoxford.ai/vision/v1.0/describe'
_key = '4474334ed4334446a378111e40e1d156' #Here you have to paste your primary key
_maxNumRetries = 10

_searchURL = 'https://bingapis.azure-api.net/api/v5/search/'
_searchKey = 'facce9ec59db43ac80f9d28f3627a32f'

_spotifyURL = 'https://api.spotify.com/v1/search'

def processRequest(json, data, headers, params):
    """
    Helper function to process the request to Project Oxford

    Parameters:
    json: Used when processing images from its URL. See API Documentation
    data: Used when processing image read from disk. See API Documentation
    headers: Used to pass the key information and the data type request
    """

    retries = 0
    result = None

    while True:

        response = requests.request('post', _url, json=json, data=data, headers=headers, params=params)

        if response.status_code == 429:

            print("Message: %s" % (response.json()['error']['message']))

            if retries <= _maxNumRetries:
                time.sleep(1)
                retries += 1
                continue
            else:
                print('Error: failed after retrying!')
                break

        elif response.status_code == 200 or response.status_code == 201:

            if 'content-length' in response.headers and int(response.headers['content-length']) == 0:
                result = None
            elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str):
                if 'application/json' in response.headers['content-type'].lower():
                    result = response.json() if response.content else None
                elif 'image' in response.headers['content-type'].lower():
                    result = response.content
        else:
            print("Error code: %d" % (response.status_code))
            print("Message: %s" % (response.json()['error']['message']))

        break

    return result

def processRequestGet(url, headers, params):
    """
    Helper function to process the request to Project Oxford

    Parameters:
    json: Used when processing images from its URL. See API Documentation
    data: Used when processing image read from disk. See API Documentation
    headers: Used to pass the key information and the data type request
    """

    retries = 0
    result = None

    while True:

        response = requests.request('get', url, headers=headers, params=params)

        if response.status_code == 429:

            print("Message: %s" % (response.json()['error']['message']))

            if retries <= _maxNumRetries:
                time.sleep(1)
                retries += 1
                continue
            else:
                print('Error: failed after retrying!')
                break

        elif response.status_code == 200 or response.status_code == 201:


            if 'content-length' in response.headers and int(response.headers['content-length']) == 0:
                result = None
            elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str):
                if 'application/json' in response.headers['content-type'].lower():
                    result = response.json() if response.content else None
                elif 'image' in response.headers['content-type'].lower():
                    result = response.content
        else:
            print("Error code: %d" % (response.status_code))
            print("Message: %s" % (response.json()['error']['message']))

        break

    return result


def image2song(urlImage):

    # URL direction to image
    #urlImage = 'http://i.imgur.com/fX5WZxD.jpg'

    # Computer Vision parameters
    params = { 'maxCandidates' : '1'}

    headers = dict()
    headers['Ocp-Apim-Subscription-Key'] = _key
    headers['Content-Type'] = 'application/json'

    json = { 'url': urlImage }
    data = None

    result = processRequest( json, data, headers, params )

    #print(result['description']['captions'][0]['text'])

    imageDescription = result['description']['captions'][0]['text']

    params = { 'q' : 'site:azlyrics.com '+imageDescription + ' lyrics'}

    headers = dict()
    headers['Ocp-Apim-Subscription-Key'] = _searchKey

    result = processRequestGet(_searchURL, headers, params )

    #print(result["webPages"]['value'][0])

    songresult = result["webPages"]['value'][0]['name']
    #print(songresult)

    songresult = songresult.split('-')[1]

    #print(songresult)


    songresult = urllib.quote_plus(songresult)

    headers = dict()
    params = { 'q' : songresult, 'type' : 'track'}

    a =  processRequestGet(_spotifyURL, headers, params )

    if len(a['tracks']['items']) > 0:
        song_url = (a['tracks']['items'][0]['external_urls']['spotify'])
        print(song_url)
        return song_url, imageDescription

    else:
        return "no song found", imageDescription



class StoreHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     })
        imageURL = form['imageURL'].value

        res, desc = image2song(imageURL)

        #self.respond("uploaded %s, thanks" % res)
        #self.redirect(res)

        template = Template(FORM)
        response = template.render(description=desc, song_url=res, image_url=imageURL)

        self.respond(response)

    def do_GET(self):

        template = Template(FORM)
        response = template.render()

        self.respond(response)

    def respond(self, response, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", len(response))
        self.end_headers()
        self.wfile.write(response)

    def redirect(self, url):
        self.send_response(302)
        self.send_header("Location", url)
        self.end_headers()



FORM = """
            <html>
            <head>


            <script src="https://code.jquery.com/jquery-2.2.4.min.js"integrity="sha256-BbhdlvQf/xTY9gja0Dq3HiwQF8LaCRTXxZKRutelT44=" crossorigin="anonymous"></script>

            <!-- Latest compiled and minified JavaScript -->
            <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js" integrity="sha384-0mSbJDEHialfmuBBQP6A4Qrprq5OVfW37PRR3j5ELqxss1yVqOtnepnHVP9aJ7xS" crossorigin="anonymous"></script>

            <!-- Latest compiled and minified CSS -->
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" integrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7" crossorigin="anonymous">

            <!-- Optional theme -->
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap-theme.min.css" integrity="sha384-fLW2N01lMqjakBkx3l/M9EahuwpSfeNvV63J5ezn3uZzapT0u7EYsXMjQV+0En5r" crossorigin="anonymous">

            </head>

            <body>

            <div class="container">

            <div class="row">

            <div class="col-md-6" style="text-align:center">
            {% if image_url %}
            <img src="{{ image_url }}" class="img-rounded" width="auto" height="400px">
            {% else %}
            <img src="https://i.imgur.com/HqtEkEl.gif" class="img-rounded" width="auto" height="400px">
            {% endif %}
            </div>


            <div class="col-md-6">

            {% if song_url %}

                {% if song_url == "no song found"   %}
                    <h3 style="text-align:center">
                        sorry no song found <br>
                        try an other image
                    </h3>
                {% else %}
                <iframe src="{{ song_url }}" style="width:100%; height:400px">
                </iframe>
                {% endif %}

            {% else %}
                <iframe src="https://open.spotify.com/track/0MdMNWw0rpBjQJ4SwQ0qbg" style="width:100%; height:400px">
                </iframe>

            {% endif %}

            </div>
            </div>


            <div class row>

                <div class="col-md-6">

                    <div class="col-md-12" style="height:30px;"></div>

                    <div class="col-md-12">

                        <h5>This image can be described as:</h5>
                        {% if image_url %}
                        <h4 style="text-align:center"> "{{ description }}" </h4>
                        {% else %}
                        <h4 style="text-align:center"> "a picture of herself in a mirror" </h4>
                        {% endif %}

                    </div>

                    <div class="col-md-12" style="height:50px;"></div>


                    <div class="col-md-12">

                        <form class="form" enctype="multipart/form-data" method="post">
                            <div class="form-group">
                                <label for="exampleInputName2">Enter Image URL</label>
                                <input type="text" class="form-control" id="exampleInputName2" placeholder="https://i.imgur.com/HqtEkEl.gif" name="imageURL">
                            </div>
                            <button type="submit" class="btn btn-default pull-right">Go</button>
                        </form>

                    </div>

                </div>
                <div class="col-md-6">

                    <div class="col-md-12" style="height:30px;"></div>

                    <div class="col-md-12">

                    <a style="text-decoration: none;color: chocolate" href="javascript:DoCatPost()"> <h3> a dog is holding a cat </h3> </a>

                    <p style="font-size:16px">
                    This short example takes an image as input and uses microsoft cognitive services to
                    describe the content of that image.
                    </p>

                    <p style="font-size:16px">
                    With the description we use Bing to search a database of lyrics and match a piece of music that
                    will complement the image composition.
                    </p>

                    <p style="font-size:16px">
                    Finaly we load the song through Spotify and present it to you, just login and press play to enjoy.
                    </p>

                    </div>

                </div>

            </div>


           <script language="javascript">

            function DoCatPost(){
                $('body').load($(location).attr('href'), {imageURL:"http://thumbs.dreamstime.com/z/cat-kitten-singing-microphone-white-background-37516747.jpg" });
            }

            </script>



            </body>

            </html>
        """

def main():
    try:
        server = HTTPServer(('', 8080), StoreHandler)
        print('started...')
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down server')
        server.socket.close()
if __name__ == '__main__':
    main()

