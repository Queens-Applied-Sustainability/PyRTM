print "HEY HEY HEY"
print EWD
import subprocess
p = subprocess.Popen('./smarts295', shell=True, stdin=subprocess.PIPE,
                        cwd='exe')
p.communicate('Y')  # Use stanard mode with default input file?
