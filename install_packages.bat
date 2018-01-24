@echo off
pip install moviepy
pip install pytube
pip install beautifulsoup4
pip install twython
pip install pause
pip install psutil
echo getting ffmpeg
python %cd%\get_ffmpeg.py
echo DONE!
pause