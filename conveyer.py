import tweepy
import json
import requests
import os
from pprint import pprint
import Organize_Reports
# import tweepy.error as te
import tweepy.errors as tweepErrors
from tweepy.models import Status
from ftplib import FTP
import datetime
from operator import itemgetter
'''

onevisbnovn
        osjvnosjvn
        ojsvneojvnvosn


'''
#! CHANGE TO JSON BECAUSE THE LOCATORS ONLY WORK WITH A DIRECT LINE, SO QUOTE TWEET HANDLINF WONT WORK
#TODO: change log from .txt to .log using general logger
with open('TwitterCreds.json', 'r') as c:
    creds = json.load(c)

l = open('convLog.txt', 'w')

# Authorized for only public, read only data (Oauth2 instead of Oauth1)
auth = tweepy.OAuthHandler(creds['Consumer']['key'], creds['Consumer']['secret'])
api = tweepy.API(auth)

# ---------------------------- Check Base Entities --------------------------- #
def check_entities(like):
    """ Checks and/or retrieves info from like.entities

    Args:
        like (tweetObj): the tweet to analyze

    Returns:
        str(): screen name of user
        dict(): book of tweet info
    """    
    book = {}
    screen_name = like.user.screen_name
    entitiesDict = like.entities
    l.write(f'\n{screen_name}-------\n')
    l.write(f'-Entities\n--------\n')
    
    #! Needs improvement
    # Removes all letters not ascii
    tweetText = ''
    for letter in like.text:
        if letter.isascii():
            tweetText += letter

    l.write(tweetText + '\n')
    book.update({'text': tweetText})
    
    # Try to update book w/ ent.urls 
    try:        
        urls = like.entities['urls'][0]
        expanded_url = urls.get('expanded_url')
        book.update({'expanded_url': expanded_url})
        l.write(f'Found {len(urls.keys())} URLs\n')
        l.write(f'Expanded_url: {expanded_url}\n')
        l.write('Book updated')

    # Try to update book w/ ent.media
    except AttributeError as urlError:
        l.write(f'No Entities.urls for {screen_name}\n')
        mediaUrl = entitiesDict['media'][0].get('media_url_https')
        l.write(f'Found {entitiesDict["media"][0].get("media_url_https")}\n')
        l.write(f'Pic Url: {mediaUrl}\n')
        book.update({'media_url_https': mediaUrl})

    except IndexError:
        l.write('Index Error on Media Url\n')
    
    book.update({'hasMedia': False})
    return screen_name, book

# -------------------------- Check External Entities ------------------------- #
def check_ext_entities(like):
    """Checks like.extendedEntities for tweet info, likely for media or quote

    Args:
        like (tweetObj): tweet to analyze

    Returns:
        str(): screen name from tweet
        dict(): info from tweet
    """    
    l.write('-Extended Entities\n------\n')
    screen_name = like.user.screen_name
    book = {}
    videos = []

    try:
        media = like.extended_entities['media'][0]
        l.write('Found Ext Media\n')
    except AttributeError as ae:
        l.write(f'No extEntMedia for: {screen_name}\n')
        return screen_name, None

    thumbnail = media.get('media_url_https')
    typ = media.get('type')
    
    if typ == 'video':
        l.write('Is Video\n')
        try:
            video_info = media.get('video_info')
            duration = video_info.get('duration_millis')/1000
            l.write(f'Found dur [{duration}] and vid info [len:{len(video_info.keys())}]\n')
        
            for v in video_info.get('variants'):
                vBook = {
                    'bitrate': v.get('bitrate'),
                    'url': v.get('url'),
                    'content_type': v.get('content_type')
                }
                if v.get('bitrate'):
                    videos.append(vBook)
                    book.update({'mediaUrl': v.get('url')})
                l.write('vBook appended to videos\n')

            book.update({
                'thumbnail': thumbnail,
                'hasMedia': True,
                'type': typ,
                'duration': duration,
                'videos': videos         
            })
        except AttributeError as ae:
            print('Attr. Error')
            l.write('Cant Find "video_info"\n')

    elif typ == 'photo':
        l.write('Is Photo\n')
        book.update({
            'hasMedia': True,
            'type': typ,
            'mediaUrl' : media.get('media_url_https')
            })
    return screen_name, book

# -------------------------------- Quote Tweet ------------------------------- #
def check_quote(like):
    """ Checks for the presense of tweet.is_qted_status or like.is_rply_2_status

    Args:
        like (tweetObj): tweet obj to check originality

    Returns:
        str(), tweetObj(): string to return tweets originality, obj to return actual tweet
    """    
    l.write('==================================\n')
    l.write(f'-----{like.user.screen_name}--------\n')
    l.write('Check Quote\n')
    convo = []
    info = {}
    if like.is_quote_status:
        quotedTweetId = like.quoted_status.id_str
        l.write('\tIs Quoted Status\n')
        l.write(f'\tOriginal Tweet ID: {like.id_str}\n')
        l.write(f'\tQuoted Tweet ID: {quotedTweetId}\n')
        try: 
            newTweet = api.get_status(quotedTweetId)
            return 'quoted', newTweet
        except tweepy.TweepError as te:
            print('cant see quoted status')
            print(te.args)

    elif like.in_reply_to_status_id_str:
        ogTweetId = like.in_reply_to_status_id_str
        l.write('\tIs a reply Status\n')
        l.write(f'\tReply Tweet ID: {like.id_str}\n')
        l.write(f'\tOriginal Tweet ID: {ogTweetId}\n')
        try: 
            newTweet = api.get_status(ogTweetId)
            # originality, nextTweet = check_quote(newTweet)
            
            # convo.append(nextTweet)
            
            return 'replied', newTweet
        except tweepErrors.Forbidden as te:
            print(f'tweet og:({like.id_str}), new: {ogTweetId} is Forbidden')
            return None
        except tweepErrors.NotFound as nf:
            print(f'tweet og:({like.id_str}), new: {ogTweetId} is Not Found')
            return None
            
    else:
        tweetID = like.id_str
        l.write(f'\tReturned Original Tweet: {tweetID}\n')
        return 'original', like

# -------------------------------- Add To Book ------------------------------- #
def make_final_book(book, screen_name):
    """Adds a given book to the main book under screen name

    Args:
        book (dict): convBook to hold all other books
        entType (str): type of sub book (ent or ext)
        entBook (dict): subbook to add to convBook
        screen_name (str): screen name of tweet author
        
    Returns:
        book (dict): completed book        
    """    
    screen_name, entBook = check_entities(result)
    screen_name, extBook = check_ext_entities(result)
    tweetInfo = get_info(result)
    if entBook:
        fullInfoBook = entBook | tweetInfo
    elif extBook:
        fullInfoBook = extBook | tweetInfo
    else:
        fullInfoBook = tweetInfo
    return fullInfoBook
    
    # if isinstance(entBook, dict):
    #     l.write(f'\n** Adding {entBook.keys()}\n________________________\n')
    #     book.get(screen_name).append(entBook)
    #     return book
    # else:
    #     try:
    #         book.get(screen_name).append(entBook)
    #         return book
    #     except Exception as e:
    #         print(e)
        
# ---------------------------- Dict Of Tweet Info ---------------------------- #
def get_info(like):
    """ Compiles an info dict from import tweet values

    Args:
        like (tweetObj): tweet to analyze

    Returns:
        dict(): book of important tweet values
    """    
    info = {}
    info['id_str'] = like.id_str
    info['text'] = like.text
    info['name'] = like.user.name
    info['screen_name'] = like.user.screen_name
    info['created_at'] = str(like.created_at)
    info['favorite_count'] = like.favorite_count
    info['retweet_count'] = like.retweet_count
    info['in_reply_to_status_id_str'] = like.in_reply_to_status_id_str
    try:        
        info['quoted_status.id_str'] = like.quoted_status.id_str
    except Exception as e:
        pass
    # print(like.user.screen_name)
    try:
        mentions = like.entities.get('user_mentions')
        userMentions = {
            'screen_name': mentions[0].get('screen_name'),
            'id_str': mentions[0].get('id_str')
        }
        info.update({'user_mentions': userMentions})
    except IndexError as ie:
        # .mentions exists, but empty
        pass
    except AttributeError as ae:
        # .mentions doesnt exist
        pass
    return info

def fill_book(result, tweetList):
    """ Function to test the originality of 'result' tweet then handle recursion
        if og:
            rtn book, list
        elif reply:
            newTweet = fill_book(newResult, old tweetList)
        elif qoute:
            newTweet = fill_book(newResult, old tweetList)
        else:
            failure, fix later
            
    Args:
        result (tweet Obj): tweet to use logic on
        tweetList (list): list of tweetObj

    Returns:
        _type_: _description_
    """    
    
    try:
        originiality, newTweet = check_quote(result)
    except TypeError as te:
        l.write('Couldnt check quote')
        return None
    
    firstScreenName = result.user.screen_name
    secondScreenName = newTweet.user.screen_name
    # if type(result) == dict():
    #     # print('!!!!!!!!!!')
    #     # print(result.user.screen_name)
    #     # fullInfoBook = make_final_book(result, firstScreenName)
    #     # tweetList.append(fullInfoBook)
    #     # l.write(f'Made Full Book for {firstScreenName}\n')
    #     return tweetList


    # fullInfoBook = make_final_book(newTweet, firstScreenName)
    # tweetList.append(fullInfoBook)
    # Logic to sort a tweets originality, where originality=str()
    # Where recursion happens
    
    # Terminating condition
    if originiality == 'original':
        fullInfoBook = make_final_book(result, firstScreenName)
        tweetList.append(fullInfoBook)
        
        return tweetList #! termination condition

    # First recursion case
    elif originiality == 'quoted':
        # originiality, newTweet = check_quote(result)
        l.write('is quoted\n')
        fullInfoBook = make_final_book(newTweet, newTweet.user.screen_name)
        tweetList.append(fullInfoBook)
        nextTweet = fill_book(newTweet, tweetList) #! Run fill_book() -> tweetBook{}
        # tweetList.append(nextTweet)

    # Second recurion case
    elif originiality == 'replied':
        l.write('is a reply\n')
        # originiality, newTweet = check_quote(newTweet)
        fullInfoBook = make_final_book(newTweet, newTweet.user.screen_name)
        tweetList.append(fullInfoBook)
        nextTweet = fill_book(newTweet, tweetList)
        # tweetList.append(nextTweet)
        
    # tweetList.append(newTweet)
    return tweetList
    # print(firstScreenName)
    # print(f'Len of Tweet List {len(tweetList)}')

# ------------------------------- MAIN PROGRAM ------------------------------- #
mainBook = {}

results = api.get_favorites(screen_name='hiddenyang1', count = 40)

# For tweet obj in returned objs from favorites
for result in results:
    convoList = []  # Create list to renew for each result

    # Hopefully return a list of tweetinfo Dicts
    fullBook = fill_book(result, convoList)
    
    if isinstance(fullBook, list):
        l.write(f'!Len(ConvoList) = {len(convoList)}\n')
        
        # for likeinfoObj in fullBook List
        for like in fullBook:
            sn = like.get('screen_name')
            
            # Try to update existing dict entry; else create new entry
            try:
                mainBook[sn].append(like)
            except KeyError as ke:
                print('keyError' + sn)
                mainBook[sn] = [like]
            
    else:
        print(f'Type(FullBook): {type(fullBook)}')
        l.write(f'Is not a Tuple- is type: {type(fullBook)}\n')
        
print(type(mainBook))
print(len(mainBook))

with open('convBook.json', 'w') as cb:
    json.dump(mainBook, cb, indent=2)          
print(f'# Likes: {len(results)}')
print(f'# keys in book: {len(mainBook)}')
l.close()

# Using ./Organize_Reports.py to create folders
basePath = r'C:\Users\User\Documents\Programming\Python_stuff\twitLikeStorage\TwitterFiles'
ro = Organize_Reports.organize_results(basePath, 'convBook.json', api)
tweetAuthors = []
for name, tweets in mainBook.items():
    # print(f'Index: {name}\nType(Value): {type(tweets)}')
    for tweet in tweets:
        fileName = ro.sort_results(tweet, name)
        tweetAuthors.append(name)
    
print(tweetAuthors)
ro.l.close()

""" Code to save JSON filesn

with open(f'TwitterResults\\Like_{screen_name}.json', 'w') as file:
    json.dump(like._json, file, indent=2)
    
#! Possible Solution to stacking tweets by author
# Python3 code to demonstrate working of
# Get values of particular key in list of dictionaries
# Using map() + itemgetter()
from operator import itemgetter

# initializing list
test_list = [{'gfg' : 1, 'is' : 2, 'good' : 3},
             {'gfg' : 2}, {'best' : 3, 'gfg' : 4}]

# printing original list
print("The original list is : " + str(test_list))

# Using map() + itemgetter()
# Get values of particular key in list of dictionaries
res = list(map(itemgetter('gfg'), test_list))

# printing result 
print("The values corresponding to key : " + str(res))

"""