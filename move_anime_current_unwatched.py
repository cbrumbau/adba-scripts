#!/usr/bin/python
import os, subprocess, sys, time

copy_exe = r"C:\Program Files\TeraCopy\TeraCopy.exe"
copy_command = "Move"
anime_path = r"H:\Current Season - To Watch"

info = subprocess.STARTUPINFO()
info.dwFlags = 1
info.wShowWindow = 6

for i in range(1, len(sys.argv)):
	filename = os.path.basename(sys.argv[i])
	command = '"' + copy_exe + '" ' + copy_command + ' "' + sys.argv[i] + '" "' + anime_path + '" /Close'
	subprocess.Popen(command, startupinfo=info)
	if i == 1:
		time.sleep(1)
