#!/usr/bin/python
#20170913:232732

import argparse
import os
import os.path as osp
import sys
import subprocess
import re
from json import loads
from urllib import quote
from colors import bcolors
    
def duration(file, precision = 3):
  result = subprocess.Popen(' '.join(['ffprobe', '-print_format json', '-show_format', re.escape(file)]),
  													stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = True)
  output = ''.join(result.stdout.readlines())
  meta = loads(output[output.find('{') : output.rfind('}') + 1])
  duration = float(meta['format']['duration'])
  duration = round(duration, precision) * 10 ** precision
  return int(duration)

def error(message):
	print >> sys.stderr, bcolors.ERROR + "[ERROR] "+ bcolors.RESET + "{}".format(message)
	exit(0)

def validate(directory):
	if not osp.exists(directory):
		error("Directory {} does not exist".format(directory))

def info(message):
	if verbose:
		print bcolors.INFO + "[INFO] " + bcolors.RESET + "{}".format(message)

video_extensions = ['.mp4']

def is_video(file):
	return osp.splitext(file)[1] in video_extensions
	
parser = argparse.ArgumentParser(description = "Create VLC playlist")
parser.add_argument("-d", "--directory", default = os.getcwd(), help = "directory containing videos")
parser.add_argument("-n", "--name", help = "name of the playlist")
parser.add_argument("-v", "--verbose", default = False, action="store_true", help="verbose")

args = parser.parse_args()

directory = args.directory.rstrip('/')
name = args.name if args.name else osp.basename(directory)
verbose = args.verbose

info("Entering directory {}".format(directory))
validate(directory)

files = [osp.relpath(osp.join(dirpath, file), directory) for (dirpath, dirnames, filenames) in os.walk(directory) for file in filenames]
info("Finding video files")
videos = filter(is_video, files)
videos.sort()
number_of_videos = len(videos)
info("{} video/s found".format(number_of_videos))

if number_of_videos == 0:
	error("No videos found")

try:
	info("Creating playlist {}".format(name + '.xspf'))
	playlist = open(directory + '/' + name + '.xspf', 'w')
except IOError:
	error("Permission denied")

info("Writing into playlist")
playlist.write('<?xml version="1.0" encoding="UTF-8"?>\n')
playlist.write('<playlist xmlns="http://xspf.org/ns/0/" xmlns:vlc="http://www.videolan.org/vlc/playlist/ns/0/" version="1">\n')
playlist.write('\t<title>Playlist</title>\n')
playlist.write('\t<trackList>\n')

for i in range(number_of_videos):
	info("Video {} of {} : {}".format(i + 1, number_of_videos, videos[i]))
	playlist.write('\t\t<track>\n')
	playlist.write('\t\t\t<location>./{}</location>\n'.format(quote(videos[i])))
	playlist.write('\t\t\t<duration>{}</duration>\n'.format(duration(osp.abspath(directory + os.sep + videos[i]))))
	playlist.write('\t\t\t<extension application="http://www.videolan.org/vlc/playlist/0">\n')
	playlist.write('\t\t\t\t<vlc:id>{}</vlc:id>\n'.format(i))
	playlist.write('\t\t\t</extension>\n')
	playlist.write('\t\t</track>\n')

playlist.write('\t</trackList>\n')
playlist.write('\t<extension application="http://www.videolan.org/vlc/playlist/0">\n')

for i in range(number_of_videos):
	playlist.write('\t\t\t<vlc:item tid="{}"/>\n'.format(i))
	
playlist.write('\t</extension>\n')
playlist.write('</playlist>\n')
playlist.close()
