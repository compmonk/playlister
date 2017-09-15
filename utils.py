import subprocess
import json
import re
import sys
from colors import bcolors

def duration(file, precision = 3):
  result = subprocess.Popen(' '.join(['ffprobe', '-print_format json', '-show_format', re.escape(file)]),
  													stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = True)
  output = ''.join(result.stdout.readlines())
  meta = json.loads(output[output.find('{') : output.rfind('}') + 1])
  duration = float(meta['format']['duration'])
  duration = round(duration, precision) * 10 ** precision
  return int(duration)
  
def error(message):
	print >> sys.stderr, bcolors.ERROR + "[ERROR] "+ bcolors.RESET + "{}".format(message)
	exit(0)

def info(message, verbose = True):
	if verbose:
		print bcolors.INFO + "[INFO] " + bcolors.RESET + "{}".format(message)
		
def warning(message):
	print bcolors.WARNING + "[WARNING] " + bcolors.RESET + "{}".format(message)
