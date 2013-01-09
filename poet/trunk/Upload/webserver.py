import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
#import pri

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("upload.html"):
                f = open(curdir + sep + self.path) #self.path has /test.html
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return
            else:
                #self.send_error(403,'File Not Found: %s' % self.path)
                #or maybe I can just server upload.html no matter what they ask for...
                
#            if self.path.endswith(".esp"):   #our dynamic content
#                self.send_response(200)
#                self.send_header('Content-type',	'text/html')
#                self.end_headers()
#                self.wfile.write("hey, today is the" + str(time.localtime()[7]))
#                self.wfile.write(" day in the year " + str(time.localtime()[0]))
#                return
                
            return
                
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)
     

    def do_POST(self):
        global rootnode
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                query = cgi.parse_multipart(self.rfile, pdict)
            self.send_response(301)
            
            self.end_headers()
            upfilecontent = query.get('upfile')

            self.wfile.write("query's type: "+type(query))
            self.wfile.write("ctype: "+str(ctype))
            self.wfile.write("pdict: "+str(pdict))
            self.wfile.write("Items found: "+len(upfilecontent))

            #print "filecontent", upfilecontent[0]
            #f = open('uploaded.xml', 'w')
            #f.write(upfilecontent[0])
            #f.close
            f = open('../../alissa/GroupMind/webroot/GroupMind/uploaded.xml', 'w')
            f.write(upfilecontent[0])
            f.close
            self.wfile.write("<HTML>Upload succeeded. You may now import your file in GroupMind.<BR><BR>");
            self.wfile.write(upfilecontent[0]);
            
        except :
            pass

def main():
    try:
        server = HTTPServer(('', 8080), MyHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()

