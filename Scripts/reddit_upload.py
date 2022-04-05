import argparse
from urllib import response
from xmlrpc.client import DateTime
import requests
import os
from convert import convertFile
import config as c
import hashlib
from threading import Thread
import praw
import prawcore.exceptions
from imgurpython import ImgurClient
from time import time

def reddit_upload(sub, title, link, retry):
    try:
        post = sub.submit(title, url=link)
        print("On Reddit here: https://www.reddit.com/r/{0}/comments/{1}/{2}/".format( sub.display_name, post.id,"_".join(post.title.split()) ) )  
    except praw.exceptions.APIException as e:
        print(e)
        print("Failed to post to {0}".format(sub.display_name))
        print("Go to: https://www.reddit.com/r/{0}".format(sub.display_name))
        if retry > 0:
            reddit_upload(sub, title, link, retry-1)
    
def apiSetup():
    # Login to Imgur and Reddit
    client_id,client_secret,user_agent,username,password=c.REDDIT
    reddit = praw.Reddit(client_id=client_id,client_secret=client_secret,user_agent=user_agent,username=username,password=password)
    reddit.validate_on_submit = True
    print('logged in to Reddit as: '+reddit.user.me().name)
    client_id, client_secret, username = c.IMGUR
    imgur = ImgurClient(client_id, client_secret)
    print("Logged in to Imgur as: "+str(imgur.get_account(username).id))
    print(f"{imgur.credits['ClientRemaining']} credits remaining")
    return reddit, imgur

def interpretTags(tags):
    # In the config you'll have a dictionary of keys of subreddits names
    subreddits = list()
    for tag in tags.split(','):
        if tag.lower() in c.CATEGORIES.keys():
            subreddits+=list(c.CATEGORIES[tag])
        elif tag in c.ALL:
            subreddits.append(tag)
        else:
            print("Invalid tag: {0}".format(tag))
    return subreddits

def upload_image(file, tags, title, description=None):
    link = None
    if file[0:4] == 'http': 
        link = file
        file = "temp.jpg" 
    base, ext = os.path.splitext(file)
    reddit, imgur = apiSetup()

    subredditlist = interpretTags(tags)
    print(subredditlist)
    subreddits = [reddit.subreddit(a) for a in subredditlist if a != '']
    config = {'name': title,'title': title,'description': description}

    if ext in c.FILE_EXTENSIONS or ext in c.VID_EXTENTIONS:
        if link is None:
            print("Uploading image")
            image = imgur.upload_from_path(file, config=config, anon=True)
            link = image['link']
            print("Image uploaded: "+link)

        print("Posting to Reddit... ")
        threads = []
        for subreddit in subreddits:
            t = Thread(target=reddit_upload, args=(subreddit,title, link, 1,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        try:
            newname = 'Posts/redditpost_{0}.{1}'.format(time.time().format('%Y%m%d-%H%M%S'), ext)
            os.rename(file, newname)
            print("File renamed to: "+newname)
        except FileNotFoundError:
            print("file name wasn't there: {0}".format(file))   
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
