#!/usr/bin/env python3
import os, pprint, re, subprocess, sys, time
import pprint
import adba

copy_exe = r"C:\Program Files\TeraCopy\TeraCopy.exe"
copy_command = "Move"
ignore_dirs = ["commentary", "pv", "youtube", "psp thumbnails"]
do_not_compare = ["commentary", "pv", "extras", "specials", "summer specials"]
ignore_extensions = [".db", ".ini", ".jpg", ".jpeg", ".png", ".mp3", ".flac"]
target_path = r"F:\Anime - Renamed"
log_file = "output_log.txt"
one_file_per_directory = True

info = subprocess.STARTUPINFO()
info.dwFlags = 1
info.wShowWindow = 6
username = "Agvir"
password = "oOwW0abcxyz"
files_with_titles = list()
titles = list()

def sanitizeFilename(name):
	# Deal with " * : < > ? \ / |
	name = re.sub('"', "\u02ba", name) # Convert double quote to double prime (U+02BA)
	name = re.sub("\*", "\uff0a", name) # Convert asterisk to full width asterisk (U+FF0A)
	name = re.sub(":", "\u02d0", name) # Convert colon to IPA triangular colon (U+02D0)
	name = re.sub("<", "\u02c2", name) # Convert less than to left arrowhead (U+02C2)
	name = re.sub(">", "\u02c3", name) # Convert greater than to right arrowhead (U+02C3)
	name = re.sub("\?\?", "\u2047", name) # Convert question mark with question mark to double question mark (U+2047)
	name = re.sub("\?!", "\u2048", name) # Convert question mark with exclamation mark to question exclamation mark (U+2048)
	name = re.sub("!\?", "\u2049", name) # Convert exclamation mark with question mark to exclamation question mark (U+2049)
	name = re.sub("\?", "\uff1f", name) # Convert question mark to full width question mark (U+FF1F)
	name = re.sub("/", "\u2044", name) # Convert forward slash to fraction slash (U+2044)
	name = re.sub(r"\\", "\u2216", name) # Convert back slash to set minus (U+2216)
	name = re.sub("\|", "\u23aa", name) # Convert pipe to curly bracket extension (U+23AA)
	# Remove trailing white spaces and periods for folders
	name = re.sub("[ \.]+$", "", name)
	return name

# Establish connection to AniDB
sys.stderr.write("Connecting to AniDB...\n")
connection = adba.Connection(commandDelay=2.1)
try:
	connection.auth(username, password)
except Exception as e :
	print(("exception msg: " + str(e)))
	sys.exit(1)

# Recursively identify all folders, move extras folders separately
filelist = list()
ignored_dir = list()
ignored_ext = list()
skip_file = list()
for i in range(1, len(sys.argv)):
	# Recursively check target directory for valid files to copy, generate file and destination array
	if os.path.isdir(sys.argv[i]):
		this_dir = sys.argv[i]
		# Process all files by directory, if any, and recurse subdir
		for dirpath, dirnames, filenames in os.walk(this_dir):
			this_dir = dirpath.split(os.sep)[-1]
			# Skip ignored directories
			if any(this_dir.lower() in ignored for ignored in ignore_dirs):
				ignored_dir.append(dirpath)
				continue
			# Skip ignored extensions
			for filename in filenames:
				# Ignore by file extension
				if any(os.path.splitext(filename)[1].lower() == ignored for ignored in ignore_extensions):
					ignored_ext.append(os.path.normpath(dirpath + os.sep + filename))
					skip_file.append(filename)
			# Skip empty directories
			if len(filenames) == 0:
				continue
			# Add individual files to file list, unless only checking one file per directory
			if one_file_per_directory:
				filelist.append([os.path.normpath(dirpath + os.sep + filename) for filename in filenames if filename not in skip_file])
			else:
				filelist.extend([os.path.normpath(dirpath + os.sep + filename) for filename in filenames if filename not in skip_file])

# Print ignored directories and extensions to file
if not os.path.exists(target_path):
	os.makedirs(target_path)
log = open(os.path.normpath(target_path + os.sep + log_file), "w", encoding="utf-8")
log.write("# Ignored directories" + "\n")
for this_dir in ignored_dir:
	log.write(this_dir + "\n")
log.write("# Ignored extensions" + "\n")
for this_file in ignored_ext:
	log.write(this_file + "\n")

# First find show title in AniDB, else skip file
changed = list()
sys.stderr.write("Identifying files in AniDB...\n")
requested_fields = list(["romaji_name"])
maper = adba.aniDBmaper.AniDBMaper()
maperFileF = set(maper.getFileMapF())
maperFileA = set(maper.getFileMapA())
requestF = list(maperFileF & set(requested_fields))
requestA = list(maperFileA & set(requested_fields))
log.write("# Directories with different titles" + "\n")
if connection.authed():
	for file in filelist:
		this_file = file
		if one_file_per_directory:
			for index in range(len(file)):
				this_file = file[index]
				try:
					episode = adba.Episode(connection, filePath=this_file, load=True, paramsF=requestF, paramsA=requestA)
					break
				except:
					sys.stderr.write("ERROR: " + this_file + " not in AniDB!\n")
					continue
		else:
			try:
				episode = adba.Episode(connection, filePath=this_file, load=True, paramsF=requestF, paramsA=requestA)
			except:
				sys.stderr.write("ERROR: " + this_file + " not in AniDB!\n")
				continue
		# pprint.pprint(vars(episode))
		# Sanitize name for a folder name
		new_title = sanitizeFilename(str(getattr(episode, "romaji_name")))
		# Compare old directory to new directory name, record differences
		old_title = os.path.basename(os.path.dirname(this_file))
		if old_title != new_title and old_title not in changed:
			changed.append(old_title)
			log.write(os.path.dirname(this_file) + "\t" + os.path.normpath(target_path + os.sep + new_title) + "\n")
		# if old_title != new_title:
			# changed.append((os.path.dirname(this_file), os.path.normpath(target_path + os.sep + new_title)))
		if one_file_per_directory:
			sys.stderr.write(str(getattr(episode, "romaji_name")) + "\n")
		else:
			sys.stderr.write(os.path.basename(this_file) + "\t" + str(getattr(episode, "romaji_name")) + "\n")
		# Add to tuple list of file with target folder
		if one_file_per_directory:
			for each_file in file:
				files_with_titles.append((each_file, new_title))
		else:
			files_with_titles.append((this_file, new_title))
log.close()

# Check if folder already exists, otherwise make new folder
sys.stderr.write("Generating folders for files if required...\n")
for file, title in files_with_titles:
	if not os.path.exists(target_path + os.sep + title):
		os.makedirs(target_path + os.sep + title)

# Move all files to folders
sys.stderr.write("Moving files to appropriate folders...\n")
for file, title in files_with_titles:
	command = '"' + copy_exe + '" ' + copy_command + ' "' + file + '" "' + os.path.normpath(target_path + os.sep + title) + '" /Close'
	subprocess.Popen(command, startupinfo=info)
	if i == 1:
		time.sleep(1)

sys.stderr.write("\nDone! Press enter to exit.\n")
input()
sys.exit(0)