#!/usr/bin/python
#20170913:232732

import argparse
import os
import os.path as osp
import sys
import subprocess
import re
import urllib
from utils import duration, info, error, warning
    	
def validate(directory):
	if not osp.exists(directory):
		error("Directory {} does not exist".format(osp.abspath(directory)))


def is_video(file):
	video_extensions = ['.mp4']
	return osp.splitext(file)[1] in video_extensions


def create(directory, name, verbose):
	validate(directory)
	info("Entering directory {}".format(directory), verbose = verbose)
	files = [osp.relpath(osp.join(dirpath, file), directory) for (dirpath, dirnames, filenames) in os.walk(directory) for file in filenames]
	info("Finding video files", verbose)
	videos = filter(is_video, files)
	videos.sort(key = lambda file: int(filter(str.isdigit, file)))
	number_of_videos = len(videos)
	info("{} video/s found".format(number_of_videos), verbose = verbose)

	if number_of_videos == 0:
		error("No videos found")

	try:
		info("Creating playlist {}".format(osp.abspath(directory + os.sep + name + '.xspf')), verbose = verbose)
		playlist = open(osp.abspath(directory + os.sep + name + '.xspf'), 'w')
	except IOError:
		error("Permission denied")

	info("Writing into playlist", verbose = verbose)
	playlist.write('<?xml version="1.0" encoding="UTF-8"?>\n')
	playlist.write('<playlist xmlns="http://xspf.org/ns/0/" xmlns:vlc="http://www.videolan.org/vlc/playlist/ns/0/" version="1">\n')
	playlist.write('\t<title>Playlist</title>\n')
	playlist.write('\t<trackList>\n')

	count = 0
	for i in range(number_of_videos):
		try:
			info("Found video {} of {} : {}".format(i + 1, number_of_videos, videos[i]), verbose = verbose)
			video = urllib.quote(videos[i])
			length = duration(osp.abspath(directory + os.sep + videos[i]))
			playlist.write('\t\t<track>\n')
			playlist.write('\t\t\t<location>./{}</location>\n'.format(video))			
			playlist.write('\t\t\t<duration>{}</duration>\n'.format(length))
			playlist.write('\t\t\t<extension application="http://www.videolan.org/vlc/playlist/0">\n')
			playlist.write('\t\t\t\t<vlc:id>{}</vlc:id>\n'.format(count))
			playlist.write('\t\t\t</extension>\n')
			playlist.write('\t\t</track>\n')
			count += 1
		except KeyError:
			warning("Video {} : {} is invalid".format(i, videos[i]))
			continue		

	playlist.write('\t</trackList>\n')
	playlist.write('\t<extension application="http://www.videolan.org/vlc/playlist/0">\n')

	for i in range(count):
		playlist.write('\t\t\t<vlc:item tid="{}"/>\n'.format(i))
	
	playlist.write('\t</extension>\n')
	playlist.write('</playlist>\n')
	playlist.close()
	info("Done {} videos added to the playlist {}".format(count, name), verbose = verbose)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = "Create VLC playlist")
	parser.add_argument("-d", "--directory", default = os.getcwd(), help = "directory containing videos")
	parser.add_argument("-n", "--name", help = "name of the playlist")
	parser.add_argument("-v", "--verbose", default = False, action="store_true", help="verbose")
	args = parser.parse_args()
	directory = args.directory.rstrip('/')
	name = args.name if args.name else osp.basename(directory)
	verbose = args.verbose
	create(directory, name, verbose)
