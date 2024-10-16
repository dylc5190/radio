# -*- coding: utf-8 -*-

import os
import re
import sys
import urllib.request
import zlib
import time
import logging
import subprocess
import datetime
import getopt

prog = 'bluespower'
duration = 2*60*60
opts, args = getopt.getopt(sys.argv[1:], "p:t:h")
for o, a in opts: 
    if o == "-p":
        prog = a
    elif o in ("-t"):
        duration = int(a)
    elif o in ("-h"):
        print(sys.argv[0] + " [-p bluespower] [-t 60(seconds)] [-h]")
        sys.exit(0)

if prog != 'bluespower': sys.exit(0)
outFile = prog + '_' + time.strftime('%Y%m%d',time.localtime()) + '.ts'

logFile = 'radio.log'

logging.basicConfig(filename=logFile,level=logging.DEBUG,format="%(asctime)s: %(message)s")

def get_url():
  response = urllib.request.urlopen('https://www.e-classical.com.tw/index.html')
  page = response.read().decode('utf-8')
  found = 0
  url = None
  for line in page.split():
      if found == 1:
         m = re.search(r"\$\('#radio_src'\)\.attr\('src','(https://.+)'\);",line)
         if m:
            url = m.group(1)
            break
      else:          
          m1 = re.search(r"\$\('\.radio_onair'\)",line)
          if m1:
             found += 1
             continue
  return(url)

url = get_url()
if url is None:
    logging.info("Failed to find URL")
    sys.exit(0)

prefix = "https://eclassicalradio-hichannel.cdn.hinet.net/live/pool/hich-ra000018/ra-hls/"

logging.info("Opening URL: " + url)

headers = { 'Origin': 'https://www.e-classical.com.tw',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36',
            'Referer': 'https://www.e-classical.com.tw/index.html',
           }
lastId = 0
elapsed = 0
err = 0
t0 = time.time()
with open(outFile,'wb') as f:
  while elapsed < duration:
    elapsed = time.time() - t0
    try:
      if err:       
        url = get_url() # after error occurs, token becomes expired. need to get a new one.
      req = urllib.request.Request(url, None, headers)
      response = urllib.request.urlopen(req)
      hdr = response.getheader('Content-Type')
      if re.search(r'vnd\.apple\.mpegurl',hdr) is None:
         print("not mpegurl", hdr)
         time.sleep(1)
         continue
      hdr = response.getheader('Content-Encoding')
      page = response.read().decode('utf-8')
      if hdr == 'gzip':
         print("unzip mpegurl")
         page = zlib.decompress(page,16+zlib.MAX_WBITS)

      #with open("mpegurl."+str(t),"w+") as f1:
      #   f1.write(page)

      t1 = time.time()
      for line in page.split():
          m1 = re.search(r'(\d+)\.ts$',line)
          if m1:
             id = int(m1.group(1))
             if id <= lastId:
                print("skip {0}".format(id))
             else:
                print("record {0} ".format(id))
                url_ts = prefix+line.rstrip('\n')
                #fname = 'chunk_{0}.ts'.format(id)
                #cmd = "wget -O {0} \"{1}\"".format(fname,url_ts)
                #print cmd
                #os.system(cmd)
                #print "done"
                print("GET {0} ... ".format(url_ts))
                req = urllib.request.Request(url_ts, None, headers)
                f.write(urllib.request.urlopen(req,timeout=10).read())
                print("done")
                lastId = id
          else:
             m1 = re.search(r'(hich-ra000018.+m3u8.+)$',line)
             if m1:
                url = prefix + m1.group(1)
                break
      pause = 5 - (time.time() - t1)
      if pause > 0: time.sleep(pause)
      err = 0
    except Exception as e:
      time.sleep(1)
      err += 1
      if err < 10 or err % 60 == 0:
        logging.error(e)

logging.info("Exit")
