#!/afs/nd.edu/user15/pbui/pub/anaconda2-4.1.1/bin/python2.7

##########################################################################################
#                                                                                        #
#   Python script for Twitter Meme Bot                                                   #
#                                                                                        #
#   Created by Mimi Chen                                                                 #
#   November 17, 2016                                                                    #
#                                                                                        #
#   Twitter Meme Bot is a an AI bot that tweets memes from the meme source "ifunny.co".  #
#                                                                                        #
##########################################################################################


##################
#    IMPORTS     #
##################

import tweepy
from matplotlib.pyplot import imread, imshow, imsave, figure
import numpy
import requests
import StringIO
import requests
import time

##################
# AUTHENTICATION #
##################

CONSUMER_KEY    = '' # INSERT CONSUMER KEY
CONSUMER_SECRET = '' # INSERT CONSUMER SECRET

ACCESS_TOKEN    = '' # INSERT ACCESS TOKEN
ACCESS_SECRET   = '' # INSERT ACCESS SECRET TOKEN


auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api  = tweepy.API(auth)

#################
#   FUNCTIONS   #
#################

# Image functions written by Professor Peter Bui at University of Notre Dame
# (http://www3.nd.edu/~pbui/teaching/cdt.30010.fa16/notebook10.html)

# Display figures and images inline

def display_image(image, enlarge=False):
    ''' Display image (enlarge if specified) '''
    if enlarge:
        figure(figsize=(10, 8))
    imshow(numpy.asarray(image).astype('uint8'))

def read_image(path, format='JPG'):
    ''' Read image from path or URL '''
    if path.startswith('http'):
        data  = StringIO.StringIO(requests.get(path).content)
        image = imread(data, format=format)
    else:
        image = imread(path)
    return image

def save_image(path, image):
    ''' Save image to specified path '''
    imsave(path, numpy.asarray(image).astype('uint8'))


# Function to generate meme_database
def generate_meme_database(URL):
    '''Returns an array of meme URLs given the meme source website's URL '''

     # Get page content from the meme source URL
    result = requests.get(URL)

     # Create an array to hold all URLs of memes
    database = []

     # Figure out what tag the meme URL is under in HTML file
    media_tag = '<img class="media__image" src="' # all meme images from ifunny.co begin with this string tag 

     # Get content of requested page as a string    
    data = result.content 

     # Locate all the URLs of memes in page source code
    while (data):
         # Find returns the index of where '<' of image tag is
         # Index is shifted by the length of "media_tag" so index now points at begining of URL
         index = data.find(media_tag) + len(media_tag)

         # If the media_tag no longer appears in the data, no need to keep looking through the data
         if data.find(media_tag) < 0:
             break
         
         # Desired data now begins with the meme url
         data = data[index:]
         stuff = data.split("\"") # data is not changed; stuff is a list holding all strings separated by a "
         meme_url = stuff[0] # Meme url should be the first element of stuff
         
         # Add to the meme database
         database.append(meme_url)
    return database

# Function to retrieve meme URL and tweet meme image
def meme_bot(meme_database):
    '''Retrieves the memes using the URLs in the meme database, saves memes to the path "todaysmeme.jpg", 
    and uses the Twitter API to tweet the memes'''

    wait_time = 600.0 # 10 minutes

    # While the meme_database is not empty

    for index in range(len(meme_database)):
        # Pull image from meme URL and save to local computer to the path called 'todaysmeme.jpg'
        # 'todaysmeme.jpg' will be overwritten with new meme with each iteration
        print 'Number {} of {} memes in database'.format(index+1, len(meme_database))
        print 'Meme url: {}'.format(meme_database[index])

        save_image('todaysmeme.jpg',read_image(meme_database[index]))

        # Try to tweet the meme; catch if there's an error 
        try:
                print 'Running bot...'
    #            display_image('todaysmeme.jpg')
                api.update_with_media('todaysmeme.jpg')
                print 'Waiting {} seconds...\n'.format(wait_time)
                time.sleep(wait_time)

        except tweepy.TweepError as e:
                print 'Houston, we have a problem: {}'.format(e)
                continue

##################
# MAIN EXECUTION #
##################

# Create a historical meme database by running meme_bot for the first time
print 'Using memes from the tag "FEATURED"\n'
HIST_MEME = generate_meme_database('https://ifunny.co')
meme_bot(HIST_MEME)

while True:
    print '\n**GENERATING NEW MEME DATABASE**\n'
    # Load memes from the "featured" page of ifunny
    meme_database = generate_meme_database('https://ifunny.co')

    # If memes from "featured" page of ifunny have already been tweeted, use memes from the tag "meme" on ifunny
    if (meme_database == HIST_MEME):
        print 'Using memes from the tag "MEME"\n'
        meme_database = generate_meme_database('https://ifunny.co/tags/meme')

    else: # Using memes from "featured page"

        # Update history with the new meme_database from "featured"
        print 'Using memes from "FEATURED"\n'
        HIST_MEME = meme_database

    # Tweet memes from "meme_database"
    meme_bot(meme_database)
