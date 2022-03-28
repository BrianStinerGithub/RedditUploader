import argparse
from urllib import response
import requests
import os
from datetime import datetime
from convert import convertFile
import config as c
import praw
import hashlib

from imgurpython import ImgurClient
    
def upload(file, api, auth0):
    md5file = hashlib.md5(open(file, 'rb').read()).hexdigest()
    response = requests.post(url=api, auth=auth0)
    

def apiSetup():
    # Login to Imgur and Reddit
    client_id,client_secret,user_agent,username,password=c.REDDIT
    reddit = praw.Reddit(client_id=client_id,client_secret=client_secret,user_agent=user_agent,username=username,password=password)
    reddit.validate_on_submit = True
    print('logged in to Reddit as: '+reddit.user.me().name)
    client_id, client_secret, username = c.IMGUR
    imgur = ImgurClient(client_id, client_secret)
    print("Logged in to Imgur as: "+str(imgur.get_account(username).id))
    return reddit, imgur

def interpretTags(tags):
    # In the config you'll have a dictionary of keys to a string list of subreddits names
    subreddits = list(c.DEFAULT)
    for tag in tags.split(','):
        if tag in c.CATEGORIES.keys():
            subreddits+=list(c.CATEGORIES[tag])
        elif tag in c.ALL:
            subreddits.append(tag)
        else:
            print("Invalid tag: {0}".format(tag))
    return subreddits

def upload_image(file, tags, title, description=None):

    base, ext = os.path.splitext(file)
    reddit, imgur = apiSetup()

    print(interpretTags(tags))
    subreddits = [reddit.subreddit(a) for a in interpretTags(tags) if a != '']
    config = {'name': title,'title': title,'description': description}

    if file.endswith(c.VID_EXTENTIONS):
        convertFile(file)
        file = base+'.gif'
    if file.endswith(c.FILE_EXTENSIONS):
        print("Uploading Image... ")
        image = imgur.upload_from_path(file, config=config, anon=False)
        print("On Imgur here: {0}".format(image['link']))
        print("Posting to Reddit... ")
        for subreddit in subreddits:
            try:
                post = subreddit.submit(title, url=image['link'], resubmit=False)
                print("On Reddit here: https://www.reddit.com/r/{0}/comments/{1}/{2}/".format( subreddit.display_name, post.id,"_".join(post.title.split()) ) )  
            except praw.exceptions.APIException as e:
                print(e)
                print("Failed to post to {0}".format(subreddit.display_name))
    else:
        print("File not uploadable. Image or Video only.")
    print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Uploads a picture to Imgur and posts it to a list of subreddits')
    parser.add_argument('-f', '--file', type=str, help='The path to the image or gif to upload')
    parser.add_argument('-s', '--subreddits', type=str, help='The list of categories and/or subreddits to post to')
    parser.add_argument('-t', '--title', type=str, help='The title of the post')
    parser.add_argument('-d', '--description', type=str, default=None, help='The description of the post')
    args = parser.parse_args()
    print(args) 
    file, tags, title, description = args.file, args.subreddits, args.title, args.description
    
    upload_image(file, tags, title, description)
