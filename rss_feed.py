"""Quaint RSS Feed Reader

This simple tool lets the user read RSS feeds of their choice in the
terminal. There are profiles within this program the .JSON starts empty

This tool requires TinyDB and BeautifulSoup4 to be installed within the
python environment you're running this in.
"""

from bs4 import BeautifulSoup as soup
from urllib.request import urlopen, Request
from tinydb import TinyDB, Query
import re
from os import system, path
import argparse
from time import sleep

# Declaring some constants!

DIRNAME = path.dirname(__file__)

DB = TinyDB(path.join(DIRNAME, 'profiles.json'))
USER = Query()

clear = lambda: system('cls' if name=='nt' else 'clear')

def get_rss_feed(feed: str) -> bytes:

  """Gets individual RSS Feed Response

    Parameters
    ----------
    feed : str
      A valid RSS feed XML site

    Returns
    -------
      xml_page
          Site data returned as bytes by urllib
    """
  
  req = Request(feed, headers={'USER-Agent': 'Mozilla/5.0'})
  response = urlopen(req)
  xml_page = response.read()
  response.close()
  return xml_page


def read_all_feeds(feeds: list):
  """ Iterates over all user feeds an runs read_single_feed on them

  Parameters
  ----------
  feeds : list
    A list of valid RSS feed XML sites

  Returns
  -------
    prints x stories to console per feed
  """
    
  def read_single_feed(feed: str) -> list:
    """Gets individual RSS Feed Response

    Parameters
    ----------
    feed : str
      A valid RSS feed XML site

    Returns
    -------
      list
          List of strings containing RSS Feed News/stories
    """
    results = return_results(get_rss_feed(feed))
    return results
  clear()
  print('Reading Feeds \n')
  news_per_feed = input("How many news items per entry do you want? (Default 5) \n")
  try:
    news_per_feed = int(news_per_feed)
  except:
    news_per_feed = 5
  
  clear()
  print('Loading feeds \n')
  for feed in feeds:
    for i, news in enumerate(read_single_feed(feed)):
      if i == news_per_feed:
        break
      else:
        print(news)
  print("Thank you for using Quaint RSS Feed Reader")


def return_results(xml_page: bytes) -> list:
  """Creates list of data from RSS Feed

    Parameters
    ----------
    xml_page : bytes
      RSS Feed Site data returned as bytes

    Returns
    -------
      list
          list of formatted data from each news items in a RSS Feed
    """
  
  def item_message_format(item: class, channel_title: str) -> str:
    """Gets news item from RSS feed and formats it

    Parameters
    ----------
    item : 
      A bs4.element.Tag of individual news items in XML
    channel_title : str

    Returns
    -------
      str
          Formatted string from a sigle news item in a feed
    """
    
    article_title = item.title.text
    description = item.description.text[0:100]
    link = item.link.text
    publication_date = item.pubDate.text
    message = f"\n{channel_title} \n{article_title} \n{description}... \n{link} \n{publication_date} \n" 

    return message

  results = []
  soup_page = soup(xml_page, "xml")
  news_list = soup_page.findAll("item")
  channel_title = soup_page.find('channel').title.text

  for getitem in news_list:
    print(type(getitem))
    results.append(item_message_format(getitem, channel_title))

  return results


def create_account(profile_name = ''):
  """Creates user profile

    Parameters
    ----------
    profile_name : ""
      this value is taken from else where and is only '' to make it work...
      I need something better though

    Returns
    -------
      Adds a user entry in profiles.json
    """

  USER = Query()
  profile_name = input("Choose a profile Name (Please don't include spaces) \n")
  
  if " " in profile_name:
    create_account()
  
  elif DB.search(USER.name.matches(profile_name, flags=re.IGNORECASE)):
      clear()
      print(f'{profile_name} is already taken!')
      create_account()
  else:
    DB.insert({'name': profile_name, 'feeds': []})
    add_feeds(profile_name)


def add_feeds(profile_name: str):
  """Adds user inputted feeds to profiles.json

    Parameters
    ----------
    profile_name : str
      the name of the users profile

    Returns
    -------
      Updates user profile with inputted feeds
    """

  clear()
  print("Let's add some feeds \n")
  new_feeds_string = input("What RSS feeds would you like to add to your account? Please separate feeds with a comma ', ', or press n to skip: \n")
  print('\n')
  if new_feeds_string.lower() == "n":
    return 
  new_strings = new_feeds_string.split(', ')
  valid_feeds = []
  for i in new_strings:
    try: 
      return_results(get_rss_feed(i))
      valid_feeds.append(i)
      print(f"{i} was added to your feeds\n")
    except:
      print(f"{i} is not a valid feed!\n")
      sleep(2)
      add_feeds(profile_name)
  #take valid feeds and perform 
  user_search = DB.search(USER.name == profile_name)[0]
  user_feeds = user_search["feeds"]
  for i in valid_feeds:
    if i in user_feeds:
      print(f"{i} is already in your feeds!")
      sleep(2)
      add_feeds(profile_name)
    else:
      user_feeds.append(i)
  DB.update({"feeds": user_feeds}, USER.name == profile_name)


def login(profile_name: str):
  """Welcomes user and diverts user to specific functions (could be renamed)

    Parameters
    ----------
    profile_name: str
      the name of the users profile

    Returns
    -------
    N/A
    """

  search_results = DB.search(USER.name == profile_name)
  
  if len(search_results):
    clear()
    print(f'Logged in! Welcome, {profile_name}\n')
    feeds = DB.search(USER.name == profile_name)[0]["feeds"]
    print(f"You have {len(feeds)} feeds:\n")
    for i, feed in enumerate(feeds):
      print(f"{i+1}. {feed}")

    will_add_feeds = input(f"\nWould you like to add a new one? (Y/N) \n")
    if will_add_feeds.lower() == 'n':
      read_all_feeds(feeds)
    elif will_add_feeds.lower() == 'y':
      feeds = DB.search(USER.name == profile_name)[0]["feeds"]
      add_feeds(profile_name)
      read_all_feeds(feeds)


def start_login():
  """Checks if user has account after user input

  Parameters
  ----------
  N/A

  Returns
  -------
  N/A
  """

  clear()
  has_account = input('Do you have a profile? Y/N\n')

  if has_account.lower() == 'y':
    #RIGHT HERE!!
    profile_name = input('What is your profile name? (Profile name is case insensitive)\n')
    login(profile_name)

  elif has_account.lower() == 'n':
    create_account()

  else:
    print('invalid input')
    start_login()


if __name__ == "__main__":

  # Creating Parser
  parser = argparse.ArgumentParser(prog = "rss_feed")

  # Adding Arguments
  parser.add_argument('-n','--profile_name',   
                      type=str,
                      help='Skips all the prompts')

  # Executing parse_args()
  args = parser.parse_args()
  name = args.profile_name

  if (name):
    login(name)
  else:
    start_login()