# Hotels 
TripAdvisor's Hotels Scrapper for uk version of the site. This only works on city results, not on country results.

It should be safe to use on any wi-fi, as all requests made to TripAdvisor are done through proxies. Proxies are fetched from a website at the start of the scrapping.



This package is meant to be use both by using the `conf.ini` configuration file and the command-line interface.

# Installation

This installation guide has been written for linux and specifically the ubuntu distro.

## Required packages:
1. Get the following driver: 
   * [geckodriver](https://github.com/mozilla/geckodriver/releases): Software has been written for the version `0.26.0`
   * [chrome-driver](https://chromedriver.chromium.org/downloads): Software has been written for the version `80.0.3987.106`



2. Add them to a folder within your path:

   Get the list of folders in the path:

   ```bash
   $ echo $PATH
   /home/nathan/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
   ```

   Every path (colon-separated) is a possible folder. Choose one of them (preferably where sudo permission is not needed), and move the drivers to it.



## Install python Requirements

## Optional: Create a virtualenv

Run the following in the root of the projects folder:

```bash
$ virtualenv --python=python3.7 venv
$ . ./venv/bin/activate
```

## Install requirements:

Run the following:

```
$ pip3 install -r requirements.txt
```



# How to use:

 ## Conf.ini

The configuration file is in the root of the project folder, and quite a few options are adjustable here. The file should look like this one :

```reStructuredText
[TRIP_ADVISOR]
BASE_URL = https://www.tripadvisor.co.uk/Hotels-g298484-Moscow_Central_Russia-Hotels.html
EXCEL_PATH = /home/nathan/Desktop/chicago.xlsx
SAVE_DIR = /home/nathan/Projects/hotels/saves/
LOG_DIR = /home/nathan/Projects/hotels/.log/

# check on the currency changer of TripAdvisor to get the correct name & symbols
currency_wanted_symbol = £
currency_wanted_name = GBP

[PROXY_WEBSITE]
BASE_URL = https://free-proxy-list.net/

[CURRENCY_API]
TOKENS = ex1, ex2
BASE_URL = https://free.currconv.com/api/v7/
```

Here some important ones: 

- BASE_URL: the page to scrap. should start with `https://www.tripadvisor.co.uk/Hotels`

* Excel Path: path to write the result excel file
* Save dir: folder where to write the saves (one save is done each time a page is successfully scrapped)
* Log dir: where to write the log file.
* currency_wanted_symbol/currency_wanted_name: the currency in which the price must be converted.
* Currency API - TOKENS: list of tokens for the currency API.





## cli call:

In the root of the project, you can then call the following commands to scrap a TripAdvisor page (make sure your virtual env is activated !):

```bash
$python -m hotels
Usage: __main__.py [OPTIONS] COMMAND [ARGS]...

  Scrapper click group of commands.

Options:
  --help  Show this message and exit.

Commands:
  restart-from-save  Recover data from a save and start scrapping based on...
  saves              show saved files.
  scrap              Scrap a TripAdvisor page, get all pages available...

```



As stated, three commands are available:

- `scrap` to start scrapping a TripAdvisor hotel page and then carry one until the last page is reached,
- `restart-from-save` to scrap a TripAdvisor hotel page starting from a save and carry on until the last page is reached,
- `saves` to show available save file.



Each command as its own help message, which is displayed by using the `--help` flag. The command uses the `conf.ini` file as a default for its argument.