# -*- coding: utf-8 -*-

from selenium import webdriver
import os
import re
import sys
import urllib
import urllib2
import zlib
import time
import logging
import subprocess
import datetime

duration = 2*60*60

if len(sys.argv) > 1:
  prog = sys.argv[1]
  outFile = prog + '_' + time.strftime('%Y%m%d',time.localtime()) + '.ts'
  if prog == 'bluespower':
    # ra000018
    radioId = "Classical Taiwan"
  elif prog == 'music543':
    # ra000114
    radioId = "Alian"
  else:
    sys.exit(0)
else:
  sys.exit(0)

site = 'http://radio-hichannel.cdn.hinet.net'
logFile = 'radio.log'
urlInfo = 'ff.log.0' #this should sync with environment variable MOZ_LOG_FILE below
urlHiChannel = 'http://hichannel.hinet.net/'

if os.path.exists(urlInfo): os.remove(urlInfo)
os.environ["MOZ_LOG"] = "timestamp,rotate:200,nsHttp:3"
os.environ["MOZ_LOG_FILE"] = "d:/temp/ff.log"

logging.basicConfig(filename=logFile,level=logging.DEBUG,format="%(asctime)s: %(message)s")

fb = webdriver.firefox.firefox_binary.FirefoxBinary("D:/programs/Firefox36/firefox.exe")
fp = webdriver.FirefoxProfile()
browser = webdriver.Firefox(firefox_profile=fp,firefox_binary=fb)
retry = 5
while retry > 0:
  browser.get(urlHiChannel)
  time.sleep(60) #wait for advertisement to finish
  try:
    timeBegin = datetime.datetime.utcnow()
    time.sleep(1)
    browser.find_element_by_xpath("//div/p[contains(text(),'{0}')]/../preceding-sibling::a".format(radioId)).click()
    break
  except:
    retry -= 1
    logging.info("Oops. " + radioId + " is not found.")
if retry == 0: sys.exit(0)
time.sleep(10)
browser.quit()

print "search log after " + str(timeBegin)
reParam = re.compile('(/live/pool/.+?)[^/]+0.m3u8\?token1=([^&]+)&token2=([^&]+)&expire1=(\d+)&expire2=(\d+)')
matchParam = None
with open(urlInfo,'r') as f:
  for line in f:
    m = re.search(r'^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d.\d{6}',line)
    if m and datetime.datetime.strptime(m.group(0),'%Y-%m-%d %H:%M:%S.%f') >= timeBegin:
       matchParam = reParam.search(line)
       if matchParam: break

if matchParam is None:
  logging.info("Failed to find tokens")
  sys.exit(0)

url = site + matchParam.group(0)
path,token1,token2,expire1,expire2 = matchParam.groups()
prefix = site + path

headers = { 'Host': site[7:], #skip http://
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36',
            'Accept': '*/*',
            'Referer': urlHiChannel,
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4'
           }

logging.info("opening URL: " + url)

lastId = 0
f = open(outFile,'wb')
elapsed = 0
t0 = time.time()
while elapsed < duration:
    req = urllib2.Request(url, None, headers)
    try:
      response = urllib2.urlopen(req)
      hdr = response.info().getheader('Content-Type')
      if re.search(r'vnd\.apple\.mpegurl',hdr) is None:
         print "not mpegurl", hdr
         time.sleep(1)
         continue
      hdr = response.info().getheader('Content-Encoding')
      page = response.read()
      if hdr == 'gzip':
         print "unzip mpegurl"
         page = zlib.decompress(page,16+zlib.MAX_WBITS)

      #with open("mpegurl."+str(t),"w+") as f1:
      #   f1.write(page)

      t1 = time.time()
      for line in page.split():
          m1 = re.search(r'(\d+)\.ts$',line)
          if m1:
             id = m1.group(1)
             if id <= lastId:
                print "skip {0}".format(id)
             else:
                print "record {0} ".format(id)
                url_ts = prefix+line.rstrip('\n')
                #fname = 'chunk_{0}.ts'.format(id)
                #cmd = "wget -O {0} \"{1}\"".format(fname,url_ts)
                #print cmd
                #os.system(cmd)
                #print "done"
                print "GET {0} ... ".format(url_ts),
                req = urllib2.Request(url_ts, None, headers)
                f.write(urllib2.urlopen(req,timeout=10).read())
                print "done"
                lastId = id
      pause = 5 - (time.time() - t1)
      if pause > 0: time.sleep(pause)
      elapsed = time.time() - t0
    except Exception as e:
      logging.error(e)
      time.sleep(1)

f.close()

logging.info("exit.")
