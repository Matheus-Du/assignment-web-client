#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # return the status code of the response as an int
        # citation (+ for other get methods below): https://www.w3.org/Protocols/rfc2616/rfc2616-sec6.html
        code = data.split("\r\n")[0].split()[1]
        return code

    def get_headers(self,data):
        # return the headers of the response as a string
        headers = data.split("\r\n\r\n")[0]
        return headers

    def get_body(self, data):
        # return the body of the response as a string
        body = data.split("\r\n\r\n")[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        # if the command is GET, send a GET request to the server and return the response
        code = 500
        body = ""

        # parse the url
        host, port, path = self.parseURL(url)
        self.connect(host, port)

        # create and send the request
        request = "GET {} HTTP/1.1\r\nHost: {}\r\nAccept: */*\r\nConnection: close\r\n\r\n".format(path, host)
        self.sendall(request)

        # receive the response and parse it into code, headers, and body
        response = self.recvall(self.socket)
        self.close()
        # TODO: implement these functions by splitting the response (verify the format of the response first)
        headers = self.get_headers(response)
        code = self.get_code(response)
        body = self.get_body(response)

        # print the response as per requirements & return the response as an HTTPResponse object
        print("{}\n{}\n{}".format(code, headers, body))
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # if the command is POST, send a POST request to the server containing the body and return the response
        code = 500
        body = ""

        # parse the url
        host, port, path = self.parseURL(url)
        self.connect(host, port)

        # create the request and parse args
        # citation: GitHub copilot
        request = "POST {} HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\nConnection: close\r\n\r\n".format(path, host, len(args))
        if args is None:
            request += urllib.parse.urlencode("")
        else:
            request += urllib.parse.urlencode(args)

        # send the request and parse the response into code, headers, and body
        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()
        code = self.get_code(response)
        headers = self.get_headers(response)
        body = self.get_body(response)

        # print the response as per requirements & return the response as an HTTPResponse object
        print("{}\n{}\n{}".format(code, headers, body))
        return HTTPResponse(code, body)
    
    def parseURL(self, url):
        # parse the url into its components
        parsed_url = urllib.parse.urlparse(url)
        port = parsed_url.port
        host = parsed_url.hostname

        # if no port is specified, use the correct port depending on the scheme (443/80)
        if port == None and parsed_url.scheme == "http":
            port = 80
        elif port == None and parsed_url.scheme == "https":
            port = 443
        
        # set path
        path = parsed_url.path
        if parsed_url.path == "":
            path = "/"

        return host, port, path

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)
        
    def getMethod(self, url, method="GET", args=None):
        # check whether the request is a GET or POST & route accordingly
        if method == "POST":
            return self.post(url, args)
        else:
            return self.get(url)
        

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
