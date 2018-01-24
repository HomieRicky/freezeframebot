Remaking freezeframebot into a new twitter bot that will pull random videos and overlay the "You got a moon!" screen from Super Mario Odyssey

Changelog 22 January, 2018
 * Updated code to Python 3.x usage (previously used 2.7)
 * Added a quick installation script to get all the nessasary libraries (requires pip)
 * Things like search terms, exclusions, and credentials are now stored in text files rather than in code

TO USE: You need to create a twitter app at https://apps.twitter.com/ and insert the proper IDs in creds.txt


---- ORIGINAL README FROM GITHUB USER lanewinfield ----

# freezeframebot
*record scratch* *freeze frame* Yep, that's me. I'm a twitter bot that takes random youtube videos and makes them into this meme.

Because I'm a shitty developer, you have to download the libraries on your own.


You'll need:
* ffmpeg
* moviepy ~~(you're going to need to make [this edit](https://github.com/Zulko/moviepy/pull/345/files) to get exports working)~~ NO LONGER NEEDED
* pytube
* twython
* beautifulsoup (bf4)
