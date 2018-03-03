#!/usr/bin/python
import os, re, sys

file_dict = {}
subs_dict = {}
file_extension = '[avi|mkv|mp4|ogm]'
subs_extension = '[ass|ssa]'
file_regex = "\[[\w\s]+\]\s.+\s-\s(.+)\s[\(\)\[\]\w\s]+\." + file_extension
subs_regex = "\[[\w\s]+\]\s.+\s-\s(.+)\s[\(\)\[\]\w\s]+\." + subs_extension

# Process all files by directory
for i in range(1, len(sys.argv)):
	# Process passed argument
	if os.path.isdir(sys.argv[i]):
		this_dir = sys.argv[i]
		file_dict = {}
		subs_dict = {}
		# Process all files by directory, if any, and recurse subdir
		for dirpath, dirnames, filenames in os.walk(this_dir):
			# Pass 01: match all files with subs
			for filename in filenames:
				file_match = re.match(file_regex, filename)
				subs_match = re.match(subs_regex, filename)
				if file_match:
					# Strip out versioning
					id = re.sub(r'v\d$', '', file_match.group(1))
					file_dict[id] = os.path.splitext(filename)[0]
				elif subs_match:
					# Strip out versioning
					id = re.sub(r'v\d$', '', subs_match.group(1))
					subs_dict[id] = filename
			# Pass 02: Rename all subs names to file names
			for key in subs_dict.keys():
				if key in file_dict:
					# Do rename
					sub_ext = os.path.splitext(subs_dict[key])[1]
					os.rename(os.path.normpath(dirpath + os.sep + subs_dict[key]), os.path.normpath(dirpath + os.sep + file_dict[key] + sub_ext))

sys.exit(0)