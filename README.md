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

## Usage

Clone this git repository to download the necessary files and run the script:
```Shell
git clone https://github.com/thom-s/httphish
cd httphish
sudo python3 httphish.py
```

It will then ask you for the following information : 

* Whether you want to download the webpage with `wget` or if you have manually saved it to the `/web` folder. If you use `wget` it will also ask you :
    * The full URL to download (ex: `http://www.github.com/login`)
    * The IP/domain to redirect 404 requests to (ex: `www.github.com`)

You will then be prompted to press Enter to launch the HTTP server.

When you are done, simple run *cleanup.py* to delete the `/web` folder and the `post.txt` file. You will need to run this before running *httphish.py* again.

## Troubleshooting

Some websites might not work if you automatically download them but might work if you manually save them.

Some lazy-loaded content simply don't work.

If a website doesn't work, use inspect element and look under the network tab. The issue is probably some dynamic requests being broken because the site is too complex. In some cases, this can be fixed by changing the IP/domain to redirect 404 requests to. In most cases, you would have to manually modify the files and choose to not automatically download the file.

## Examples

### Working websites

* [http://www.github.com/login](http://www.github.com/login)
* [http://www.linkedin.com/](http://www.linkedin.com/)
* [http://www.facebook.com](http://www.facebook.com)
* [http://old.reddit.com/login](http://old.reddit.com/login)

### Broken websites

For most broken websites, dynamically loaded content will be the issue.

* [http://instagram.com/accounts/login](http://instagram.com/accounts/login)
* [http://www.messenger.com/login](http://www.messenger.com/login)
* [http://www.reddit.com/login](http://www.reddit.com/login)

