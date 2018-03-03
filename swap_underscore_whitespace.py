#!/usr/bin/python
import os, re, sys

for i in range(1, len(sys.argv)):
	filename = os.path.basename(sys.argv[i])
	if re.search(r'\+', filename):
		filename = re.sub(r'\+', ' ', filename)
	elif re.search(r'_', filename):
		filename = re.sub(r'_', ' ', filename)
	else:
		filename = re.sub(r' ', '_', filename)
	os.rename(sys.argv[i], os.path.normpath(os.path.dirname(sys.argv[i]) + os.sep + filename))