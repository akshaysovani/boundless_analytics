import subprocess
import re
import shlex
import os

command = "df -h"
# df = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
# df = subprocess.check_output(['df', '-h'])
# df = df.decode('utf8')
df = os.popen('df -h').read()
for line in df.split("\n"):
    if re.search("/dev/disk/by-label/DOROOT.*", line):
        disk_space = line.split()[4]
        break

percent_full = disk_space
percent_full = int(percent_full[:-1])
print(percent_full)
