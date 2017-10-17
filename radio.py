import subprocess
import time
import sys

URL = {"ksmu":["http://ksmu.streamguys1.com/ksmu3",120],
       "wncw":["http://audio-mp3.ibiblio.org:8000/wncw-128k",60],
       "kbcs":["http://www.ophanim.net:7720/stream",60]}

key = sys.argv[1]
if key not in URL: sys.exit(0)
fname = key + '_' + time.strftime('%Y%m%d',time.localtime()) + '.mp3'
url = URL[key][0]
p = subprocess.Popen(["mplayer", url, "-dumpstream", "-dumpfile", fname])
time.sleep(URL[key][1]*60)
p.terminate()

