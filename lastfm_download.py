#!/usr/bin/python

from bs4 import BeautifulSoup as BS
from pprint import pprint
from datetime import datetime
import sqlite3
from time import sleep
import urllib2

LASTFM_LOGIN = '' # Your last.fm login
LASTFM_PAGES = 0 # Number of pages in the library

with sqlite3.connect('lastfm.sqlite3') as conn:
	conn.execute('DROP TABLE IF EXISTS tracks')
	conn.execute('CREATE TABLE tracks (artist TEXT, title TEXT, timestamp INTEGER)')
	
	for page in xrange(1,LASTFM_PAGES):
		print 'Getting page %d...' % page
		for retries in xrange(1,5):
			try:
				u = urllib2.urlopen('http://www.last.fm/user/%s/library?page=%d' % (LASTFM_LOGIN, page))
				data = u.read()
				break
			except urllib2.HTTPError as e:
				print str(e)
				sleep(5)
				print 'Retrying...'

		bs = BS(data)
		track_trs = bs.select('.chartlist-name')

		for tr in track_trs:
			wrap = tr.select('.chartlist-ellipsis-wrap')
			if len(wrap) == 0:
				continue

			links = wrap[0].select('a')
			if len(links) < 2:
				continue

			track_artist = links[0].get_text().strip()
			track_title = links[1].get_text().strip()

			str_timestamp = tr.parent.get('data-timestamp')

			if str_timestamp is not None:
				track_timestamp = int(str_timestamp) 
			else:
				track_datetime = None

			conn.execute('INSERT INTO tracks VALUES (?, ?, ?)', (track_artist, track_title, track_timestamp))

		conn.commit()
		sleep(1)
		
