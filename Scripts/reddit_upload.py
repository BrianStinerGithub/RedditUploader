import argparse
import os
from datetime import datetime
from Scripts.config import VID_EXTENTIONS
from convert import convertFile
import config as c
import praw
from imgurpython import ImgurClient

def apiSetup():
    # Login to Imgur and Reddit
    client_id,client_secret,user_agent,username,password=c.REDDIT
    reddit = praw.Reddit(client_id=client_id,client_secret=client_secret,user_agent=user_agent,username=username,password=password)
    reddit.validate_on_submit = True
    print('logged in to Reddit as: '+reddit.user.me().name)
    client_id, client_secret, username = c.IMGUR
    imgur = ImgurClient(client_id, client_secret)
    print("Logged in to Imgur as: "+str(imgur.get_account(username).id))

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

    reddit, imgur = apiSetup()

    print(interpretTags(tags))
    subreddits = [reddit.subreddit(a) for a in interpretTags(tags) if a != '']
    config = {'name': title,'title': title,'description': description}
    if file.endswith(c.VID_EXTENTIONS):
        convertFile(file)
    if file.endswith(c.FILE_EXTENSIONS):

        print("Uploading Image... ")
        image = imgur.upload_from_path(file, config=config, anon=False)
        print("On Imgur here: {0}".format(image['link']))

        print("Posting to Reddit... ")
        for subreddit in subreddits:
            post = subreddit.submission(image['link'], config=config, anon=False, nsfw=True)
            print("On Reddit here: https://www.reddit.com/r/{0}/{1}".format(subreddit.display_name, post.id))      

    else:
        print("File not uploadable. Image or GIF only.")
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
