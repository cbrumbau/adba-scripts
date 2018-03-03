#!/usr/bin/python
import codecs, glob, os, re, subprocess, sys

par2j_path = r"D:\Utilities\MultiPar119\par2j.exe"
par2j_args = "c -uo -rr10 -lc3 -rd3 -up"
par2j_verify_args = "v -uo -vl1"
perform_verify = True
write_log = True
verify_only = False
find = ["Anime"]
find_regex = "^(" + "|".join(find) + ")$"

def replaceParityFolder(matchobj):
	if matchobj.group(0) in find:
		return matchobj.group(0) + ' - Parity'
	else:
		return "Parity"

delete = input("Overwrite existing parity files? (Y/N) ")
if not re.match(r'Y|N$', delete):
	sys.stderr.write("ERROR: Input not valid! Press Enter to exit.")
	input()
	sys.exit(1)

# Process all files by directory
for i in range(1, len(sys.argv)):
	sys.stderr.write("DEBUG: " + sys.argv[i] + "\n")
	# Skip if find is not found
	if len(set(find).intersection(set(sys.argv[i].split(os.sep)))) <= 0:
		sys.stderr.write("WARNING: Cannot find '" + ", ".join(find) + "' in path! Skipping " + sys.argv[i] + "!\n")
		continue
	# Process passed argument
	if os.path.isfile(sys.argv[i]):
		this_file = sys.argv[i]
		# Generate desired target dir
		target_dir = os.sep.join([re.sub(find_regex, replaceParityFolder, s) for s in os.path.dirname(this_file).split(os.sep)])
		#filename = os.path.splitext(os.path.basename(this_file))[0]
		filename = os.path.basename(this_file)
		par_file = os.path.normpath(target_dir + os.sep + filename + '.par2')
		if not verify_only:
			if not os.path.isdir(target_dir):
				try:
					os.makedirs(target_dir)
				except:
					# Raise a warning
					sys.stderr.write("WARNING: Cannot generate target directory! Skipping " + target_dir + "!\n")
					continue
			else:
				# Clean out target dir for any previous par2 file first, then generate new par2 file
				if delete == "N":
					continue
				old_files = glob.glob(os.path.normpath(target_dir + os.sep + filename + '*'))
				if delete == "N":
					if par_file in old_files:
						continue
				if old_files:
					for f in old_files:
						os.unlink(f)
			# Create par2 file
			command = par2j_path + ' ' + par2j_args + ' -d"' + os.path.dirname(this_file) +  '" "' + par_file + '" "' + this_file + '"'
			os.system(command)
		if (perform_verify):
			# Do verification
			command = par2j_path + ' ' + par2j_verify_args + ' -d"' + os.path.dirname(this_file) +  '" "' + par_file + '" "' + this_file + '"'
			if write_log:
				log_file = open(par_file + ".log", 'w')
				sys.stderr.write("\nPerforming file verification...\n\n")
				subprocess.call(command, stdout=log_file)
				log_file.close()
			else:
				os.system(command)
	elif os.path.isdir(sys.argv[i]):
		this_dir = str(sys.argv[i])
		# Process all files by directory, if any, and recurse subdir
		for dirpath, dirnames, filenames in os.walk(this_dir):
			dirpath = str(dirpath)
			# Generate desired target dir
			target_dir = os.sep.join([re.sub(find_regex, replaceParityFolder, s) for s in dirpath.split(os.sep)])
			tail = os.path.split(dirpath)[1]
			par_file = os.path.normpath(target_dir + str(os.sep) + tail + ".par2")
			if not verify_only:
				if not os.path.isdir(target_dir):
					try:
						os.makedirs(target_dir)
					except:
						# Raise a warning
						sys.stderr.write("WARNING: Cannot generate target directory! Skipping " + target_dir + "!\n")
						continue
				else:
					# Clean out target dir for any previous par2 file first, then generate new par2 file
					old_files = glob.glob(os.path.normpath(target_dir + os.sep + tail + '*'))
					if delete == "N":
						if par_file in old_files:
							continue
					if old_files:
						for f in old_files:
							os.unlink(f)
				# Create par2 file
				command = par2j_path + ' ' + par2j_args + ' -d"' + str(dirpath) +  '" "' + par_file + '" "' + '" "'.join([os.path.normpath(dirpath + str(os.sep) + str(f)) for f in filenames]) + '"'
				subprocess.call(command)
			if perform_verify:
				# Do verification
				command = par2j_path + ' ' + par2j_verify_args + ' -d"' + str(dirpath) +  '" "' + par_file + '" "' + '" "'.join([os.path.normpath(dirpath + os.sep + f) for f in filenames]) + '"'
				if write_log:
					log_file = codecs.open(par_file + ".log", 'w', 'utf-8')
					sys.stderr.write("\nPerforming file verification...\n\n")
					subprocess.call(command, stdout=log_file)
					log_file.close()
				else:
					os.system(command)

sys.stderr.write("\nDone! Press enter to exit.\n")
input()
sys.exit(0)