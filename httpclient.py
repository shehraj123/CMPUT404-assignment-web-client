#!/usr/bin/env python3
# coding: utf-8
# Copyright 2023 Shehraj Singh
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
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        
        line1 = data.split('\n')[0]
        code = re.search("\s\d\d\d\s", line1)[0].strip()
        code = int(code)

        return code

    def get_headers(self,data):

        splits = data.split('\n')
        header_list = splits[:-2]
        headers = '\n'.join(header_list)
        headers += '\n'
        return headers

    def get_body(self, data):
        
        data = data.strip()
        body = data.split('\n')[-1]
        


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
        code = 500
        body = ""

        # First we get the host and the port from the url
        urlparsed = urllib.parse.urlparse(url)
        PORT = 80
        HOST = urlparsed.netloc
        if ':' in urlparsed.netloc:
            HOST, PORT = urlparsed.netloc.split(':')
            PORT = int(PORT)

        path = urlparsed.path
        query_str = urlparsed.query
        fragment = urlparsed.fragment
        
        if query_str:
            path += '?' + query_str

        if fragment:
            path += '#' + fragment

        # Make the request
        request = 'GET /' + path + ' HTTP/1.1\r\n' \
                + 'Host: ' + HOST + ':' + str(PORT) + '\r\n' \
                + 'User-Agent: shehrajlinux/1.0\r\n' \
                + 'Connection: close\r\n' \
                + '\r\n'
                
        # Connect and send
        self.connect(HOST, PORT)
        self.sendall(request)


        # Receive the response
        response = self.recvall(self.socket)

        code = self.get_code(response)
        header = self.get_headers(response)
        body = self.get_body(response)
        
        self.socket.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        
        # First we get the host and the port from the url
        urlparsed = urllib.parse.urlparse(url)
        PORT = 80
        HOST = urlparsed.netloc
        if ':' in urlparsed.netloc:
            HOST, PORT = urlparsed.netloc.split(':')
            PORT = int(PORT)

        path = urlparsed.path
        query_str = urlparsed.query
        fragment = urlparsed.fragment 
        
        req_body = ''
        if query_str:
            req_body += query_str + '&'         
        
        if args:
            for k, v in args.items():
                k = urllib.parse.quote(k)
                v = urllib.parse.quote(v)
                req_body += k + '=' + v + '&' 

        # Now query_str has an extra '&' at the end 
        req_body = req_body[:-1]

        length = len(req_body)
       
        # Make the request
        request = 'POST ' + path + ' HTTP/1.1\r\n' \
                + 'Host: ' + HOST + ':' + str(PORT) + '\r\n' \
                + 'User-Agent: shehrajlinux/1.0\r\n' \
                + 'Content-Type: application/x-www-form-urlencoded\r\n' \
                + 'Content-Length: ' + str(length) + '\r\n' \
                + 'Connection: close\r\n\r\n' \
                + req_body + '\r\n\r\n'
                        
                
        # Connect and send
        self.connect(HOST, PORT) 
        self.sendall(request)


        # Receive the response
        response = self.recvall(self.socket)

        code = self.get_code(response)
        header = self.get_headers(response)
        body = self.get_body(response)

        print(f"\nResponse code: {code}")
        print(f"Response body: {body}")
        print(f"Response header: {header}\n\n")
        
        self.socket.close()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
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
