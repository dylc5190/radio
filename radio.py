import subprocess
import logging
import time
import sys

URL = {"ksmu":["https://ksmu.streamguys1.com/ksmu3",120],
       "wncw":["https://ice64.securenetsystems.net/WNCW",120],
       "kbcs":["http://www.ophanim.net:7720/stream",60]}

def record(key):
    key = sys.argv[1]
    if key not in URL: sys.exit(0)
    logging.basicConfig(filename='radio.log', filemode='a', level=logging.DEBUG, format='%(asctime)s %(message)s')
    fname = key + '_' + time.strftime('%Y%m%d%H',time.localtime()) + '.mp3'
    url = URL[key][0]
    p = subprocess.Popen(["mplayer", url, "-dumpstream", "-dumpfile", fname])
    stop = time.time() + URL[key][1]*60
    retry = 0
    t = 0
    while time.time() < stop and retry < 10:
      if p.poll() is not None:
         retry += 1
         time.sleep(60)
         t += 60
         fname = key + '_' + time.strftime('%Y%m%d%H',time.localtime()) + "_" + str(retry) + '.mp3'
         if key == 'wncw':
             p = subprocess.Popen(["curl", url, "-o", fname])
         else:
             p = subprocess.Popen(["mplayer", url, "-dumpstream", "-dumpfile", fname])
      time.sleep(1)
      t += 1
      if t % 300 == 0:
         logging.info("Waiting")
    p.terminate()

if __name__ == "__main__":
    record(sys.argv[1])