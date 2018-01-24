from moviepy.editor import *
from pytube import YouTube
import os, urllib, urllib3, random
from bs4 import BeautifulSoup
from twython import Twython
import imageio.plugins.ffmpeg
from datetime import datetime
from datetime import timedelta
import pause
import traceback
import psutil

# Getting credentials
creds = open('creds.txt', 'r').readlines()
APP_KEY = ''
APP_SECRET = ''
ACCESS_KEY = ''
ACCESS_SECRET = ''

for s in creds:
    if s.startswith('APP_KEY='):
        APP_KEY = s.split('=')[1].rstrip()
    elif s.startswith('APP_SECRET='):
        APP_SECRET = s.split('=')[1].rstrip()
    elif s.startswith('ACCESS_KEY='):
        ACCESS_KEY = s.split('=')[1].rstrip()
    elif s.startswith('ACCESS_SECRET='):
        ACCESS_SECRET = s.split('=')[1].rstrip()

print("Accessing Twitter with the following app key, app secret, access key, and access secret, respectively:")
print(APP_KEY)
print(APP_SECRET)
print(ACCESS_KEY)
print(ACCESS_SECRET)

# Scheduling
def round_to_next_hour(date):
    date += timedelta(seconds=60-date.second)
    #date += timedelta(minutes=60-date.minute)
    #new_date = date + timedelta(minutes=60-date.minute)
    return date

def time_str(date):
    return '{:%H:%M:%S %d/%m/%Y}'.format(date)

date = datetime.now()
print('Current time is ' + time_str(date))

failure_limit = 3

# SEARCH YOUTUBE
videoChoice = ''

exclusions = []
for f in open('exclude.txt', 'r').readlines():
    exclusions.append(f.rstrip())

def youTubeSearch():
    # choose a random dictionary word to search
    word_file = "words.txt"
    WORDS = open(word_file).read().splitlines()
    videoSearch = random.choice(WORDS);

    # search for, and randomly select YouTube videos in search
    print("SEARCHING: " + videoSearch + "\n")
    videos = []
    query = urllib.parse.quote(videoSearch)
    exclude = ('+-' + '+-'.join(exclusions)) if len(exclusions) > 0 else ''
    url = "https://www.youtube.com/results?search_query=" + query + exclude
    print(url)
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html)
    for vid in soup.findAll(attrs={'class': 'yt-uix-tile-link'}):
        videos.append('https://www.youtube.com' + vid['href'])
    videos.pop(0)
    videos = [i for i in videos if not ("channel" in i)]  # don't want channels
    videoChoice = random.choice(videos)
    print("YOUTUBE SEARCH: Downloading " + videoChoice + "\n")
    return videoChoice

def run():

    # DELETE OLD VIDEO

    try:
        os.remove('input.mp4')
    except OSError:
        pass

    try:
        os.remove('input_2.mp4')
    except OSError:
        pass

    try:
        os.remove('input_early.mp4')
    except OSError:
        pass

    try:
        os.remove('final.mp4')
    except OSError:
        pass

    # Try to download a clip
    i = 0
    videoChoice = youTubeSearch()
    yt = None

    while yt is None:
        try:
            yt = YouTube(videoChoice)
        except:
            print("YOUTUBE SEARCH: Trying again...")
            i = i + 1
            if i > 5:
                print("YOUTUBE SEARCH: Trying something else... \n")
                videoChoice = youTubeSearch()
                i = 0
            pass

    # Choose the lowest quality we can find & download
    # quality = str(yt.filter('mp4')[-1])
    video = yt.streams.filter(progressive=True, file_extension='mp4', res='360p').first().download(filename='input_early')
    print("YOUTUBE: Choosing 360p \n")

    # EDIT VIDEO

    clipArea = int(VideoFileClip("input_early.mp4").duration / 2)  # pick from the middle of the video

    # clip to 5 sec
    ffmpeg_path = imageio.plugins.ffmpeg.get_exe()
    print('ffmpeg found at ' + ffmpeg_path)

    command = ffmpeg_path+" -i input_early.mp4 -ss " + str(clipArea) + " -t 5 input.mp4"
    print("FFMPEG: Clipping down to 5 sec \n")
    os.system(command)

    # pull it in for manipulation
    clip = VideoFileClip("input.mp4")

    # add in our audio clip
    audioclip = AudioFileClip("recordscratch_vo.wav")
    comp = concatenate_audioclips([clip.audio, audioclip])

    # make that freeze frame
    endtime = clip.duration - 0.1  # the videos ffmpeg exports aren't always exact in time, this ensures we get a freeze frame as close to the end as possible
    freezeframe = clip.to_ImageClip(t=endtime)
    screensize = clip.size
    freezeclip = freezeframe.resize(height=screensize[1] * 4).resize(lambda t: 1 + 0.01 * t).set_position(
        ('center', 'center')).set_duration(8)
    freezeclip = CompositeVideoClip([freezeclip]).resize(width=screensize[0])
    freezevid = CompositeVideoClip([freezeclip.set_position(('center', 'center'))], size=screensize)\

    while clip.reader.proc.poll() is not None:
        print('b')
    while audioclip.reader.proc.poll() is not None:
        print('a')

    # combine and export video
    try:
        final_clip = concatenate_videoclips([clip, freezevid]).set_duration(13).set_audio(comp)
        print('Making final video')
        final_clip.write_videofile("final.mp4", audio_codec='aac')
    except Exception as e:
        pass
    finally:
        # cleaning up
        clip.reader.close()
        audioclip.reader.close_proc()

    clip.reader.close()
    audioclip.reader.close_proc()

    pause.seconds(5)

    # TWEET IT
    print('Sending tweet!')
    twitter = Twython(APP_KEY, APP_SECRET, ACCESS_KEY, ACCESS_SECRET)

    tweetCopy = ["*record scratch*\n*freeze frame*\nYup, that's me. You're probably wondering how I ended up in this situation."]

    video = open('final.mp4', 'rb')
    response = twitter.upload_video(media=video, media_type='video/mp4')

    tweet = twitter.update_status(status=random.choice(tweetCopy), media_ids=[response['media_id']])
    twitter.update_status(status=('@' + tweet['user']['screen_name'] + ' SOURCE VIDEO: ' + videoChoice), in_reply_to_status_id=tweet['id'])

while True:
    date = datetime.now()
    print('Current time is ' + time_str(date))
    date = round_to_next_hour(date)
    print('Next run is at ' + time_str(date))
    dt = datetime(date.year, date.month, date.day, date.hour, date.minute, date.second, 0).timestamp()
    pause.until(dt)
    fails = 0
    while fails < 3:
        try:
            run()
            break
        except Exception as e:
            fails+=1
            print("Failed!")
            traceback.print_tb(e.__traceback__)
            pass
        finally:
            active = psutil.Process(os.getpid())
            print("Theres " + str(len(active.children())) + " child processes")
            for child in active.children():
                child.kill()

    if fails == 3:
        print('Program failed 3 times at ' + time_str(date))
        #break