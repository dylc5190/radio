import subprocess
import logging
import time
import sys

URL = {"ksmu":["http://ksmu.streamguys1.com/ksmu3",120],
       "wncw":["http://audio-mp3.ibiblio.org:8000/wncw-128k",120],
       "kbcs":["http://www.ophanim.net:7720/stream",60]}

key = sys.argv[1]
if key not in URL: sys.exit(0)
logging.basicConfig(filename='radio.log', filemode='a', level=logging.DEBUG, format='%(asctime)s %(message)s')
fname = key + '_' + time.strftime('%Y%m%d',time.localtime()) + '.mp3'
url = URL[key][0]
p = subprocess.Popen(["mplayer", url, "-dumpstream", "-dumpfile", fname])
stop = time.time() + URL[key][1]*60
retry = 0
t = 0
while time.time() < stop:
  if p.poll() is not None:
     retry += 1
     fname = key + '_' + time.strftime('%Y%m%d',time.localtime()) + "_" + str(retry) + '.mp3'
     p = subprocess.Popen(["mplayer", url, "-dumpstream", "-dumpfile", fname])
  time.sleep(1)
  t += 1
  if t % 300 == 0:
     logging.info("Waiting")
p.terminate()

