#!/usr/bin/python
import os, re, sys

find = re.escape(input("Regex to search for: "))
replace = input("Replace with: ")

for i in range(1, len(sys.argv)):
	filename = os.path.basename(sys.argv[i])
	if re.search(find, filename):
		filename = re.sub(find, replace, filename)
	os.rename(sys.argv[i], os.path.normpath(os.path.dirname(sys.argv[i]) + os.sep + filename))

sys.exit(0)