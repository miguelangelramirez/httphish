# httphish
```
  _     _   _         _     _     _                   
 | |__ | |_| |_ _ __ | |__ (_)___| |__    _ __  _   _ 
 | '_ \| __| __| '_ \| '_ \| / __| '_ \  | '_ \| | | |
 | | | | |_| |_| |_) | | | | \__ \ | | |_| |_) | |_| |
 |_| |_|\__|\__| .__/|_| |_|_|___/_| |_(_) .__/ \__, |
               |_|                       |_|    |___/  
```

Quickly clone a website and launch an HTTP server to phish information with httphish.py 🐍

Only one Python 3 script with no dependencies! Simply run the script, it will automatically download a web page, host it on a local HTTP server and save all POST data sent by visitors.

Currently, it only works on simple pages with `<form>` logins. It might work on some dynamically loaded pages if they aren't too complex. Please see at the bottom of this README for examples of public websites that work and don't work.

## Prerequisites

This script currently requires the `wget` command to download websites, so this feature only works on Linux. I will probably eventually add OS detection and use Invoke-WebRequest from PowerShell on Windows, but for now, please download websites manually.

## How to use

Clone this git repository to download the necessary files and run the script:
```Shell
git clone https://github.com/thom-s/httphish
cd httphish
sudo python3 httphish.py
```

It will then ask you for the following information : 

* Whether you want to download the webpage with `wget` or if you have manually saved it to the `/web` folder. 
    * If you use `wget` it will also ask you :
        * The full URL to download (ex: `http://www.github.com/login`)
        * Whether to use the default user agent for wget or enter a custom one. (You can see the default one in the code)
    * If you want to manually download it, simply create a folder named `web` next to the script and save index.html in it.
* The IP/domain to redirect all GET/POST requests to. If any files cannot be served statically, it will HTTP forward the request there. (ex: `www.github.com`)

The `<form>` tags in index.html will then be modified to redirect requests to localhost.

You will then be prompted to press Enter to launch the HTTP server.

Browse to your own IP address (or localhost) and you will see a cloned version of the website.

Received POST and GET requests will be displayed, and POST requests coming from forms in index.html will be saved to `post.txt`. After running `httphish.py`, simply run the following command to see them : `cat post.txt`

When you are done, press CTRL+C to close the HTTP server and end the script. Before running it again, simply run *cleanup.py* to delete the `/web` folder and the `post.txt` file.

## Troubleshooting

* Some websites that do not work when you automatically download them might work if you manually save them.

* Some websites won't respond to requests directed to their IP, so try entering the domain instead (or vice-versa). 

* Some lazy-loaded content simply doesn't work.

* If a website doesn't work, use inspect element and look under the network tab. The issue is probably some dynamic requests being broken because the site is too complex. 
    * In some cases, this can be fixed by changing the IP/domain to redirect GET/POST requests to. 
    * In most cases, you would have to manually modify the files and choose to not automatically download the file.

## Website examples

### Working websites

Working websites will generally have very simple login forms and not much dynamically loaded content. Here are some I tested.

* [http://www.github.com/login](http://www.github.com/login)
* [http://www.linkedin.com/](http://www.linkedin.com/)
* [http://www.facebook.com](http://www.facebook.com)
* [http://old.reddit.com/login](http://old.reddit.com/login)

### Broken websites

For most broken websites, dynamically loaded content will be the issue. Here's some websites I found did not work.

* [http://instagram.com/accounts/login](http://instagram.com/accounts/login)
* [http://www.messenger.com/login](http://www.messenger.com/login)
* [http://www.reddit.com/login](http://www.reddit.com/login)

