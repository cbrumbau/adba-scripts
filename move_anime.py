#!/usr/bin/env python3
import os, pprint, re, subprocess, sys, time
import adba

copy_exe = r"C:\Program Files\TeraCopy\TeraCopy.exe"
copy_command = "Move"
newtype_path = r"H:\Anime"

info = subprocess.STARTUPINFO()
info.dwFlags = 1
info.wShowWindow = 6
# aniDB credentials here
username = ""
password = ""
filesWithTitles = list()
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

# Clean the session file (remove when bug is fixed)
if os.path.isfile(r"D:\Utilities\Session.cfg"):
	os.remove(r"D:\Utilities\Session.cfg")

# Establish connection to AniDB
sys.stderr.write("Connecting to AniDB...\n")
connection = adba.Connection(commandDelay=2.1)
try:
	connection.auth(username, password)
except Exception as e :
	print(("exception msg: " + str(e)))
	sys.exit(1)

# First find show title in AniDB, else skip file
sys.stderr.write("Identifying files in AniDB...\n")
requestedFields = list(["romaji_name"])
maper = adba.aniDBmaper.AniDBMaper()
maperFileF = set(maper.getFileMapF())
maperFileA = set(maper.getFileMapA())
requestF = list(maperFileF & set(requestedFields))
requestA = list(maperFileA & set(requestedFields))
if connection.authed():
	for i in range(1, len(sys.argv)):
		try:
			episode = adba.Episode(connection, filePath=sys.argv[i], load=True, paramsF=requestF, paramsA=requestA)
		except:
			sys.stderr.write("ERROR: " + sys.argv[i] + " not in AniDB!\n")
			continue
		# pprint.pprint(vars(episode))
		# Sanitize name for a folder name
		title = sanitizeFilename(str(getattr(episode, "romaji_name")))
		# Add to tuple list of file with target folder
		sys.stderr.write("Title identified as " + title + "\n")
		filesWithTitles.append((sys.argv[i], title))
else:
	sys.stderr.write("Cannot authorize connection to AniDB! Press enter to exit...\n")
	input()
	sys.exit(0)
connection.logout()

# Check if folder already exists, otherwise make new folder
sys.stderr.write("Generating folders for files if required...\n")
for file, title in filesWithTitles:
	if not os.path.exists(newtype_path + os.sep + title):
		os.makedirs(newtype_path + os.sep + title)

# Move all files to folders
sys.stderr.write("Moving files to appropriate folders...\n")
for file, title in filesWithTitles:
	filename = os.path.basename(file)
	command = '"' + copy_exe + '" ' + copy_command + ' "' + file + '" "' + newtype_path + os.sep + title + '" /Close'
	subprocess.Popen(command, startupinfo=info)
	if i == 1:
		time.sleep(1)

sys.stderr.write("\nDone! Press enter to exit.\n")
input()
sys.exit(0)