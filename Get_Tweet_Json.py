import json     # Import File Format 
import tweepy   # Import Twitter API (Application Programming Interface)

# Open Twitter Registration Credentials
with open('TwitterCreds.json', 'r') as c:
    creds = json.load(c)
    
# Open File to Save Tweet
potusFile = open('./TwitterFiles/PotusTweet.json', 'w')
    
# Sign in Using Bot Registration Credentials
auth = tweepy.OAuthHandler(
            creds['Consumer']['key'],    # Public Key
            creds['Consumer']['secret']) # Private Key
api = tweepy.API(auth)

# Get POTUS' Latest Tweet and Write it to FIle
firstTweet = api.user_timeline(screen_name='POTUS')[0]._json  
json.dump(firstTweet, potusFile, indent=2)

potusFile.close()   # Save & Close POTUS Tweet File