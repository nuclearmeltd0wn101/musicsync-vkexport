# VK to MusicSync Server Audios Exporter by MelnikovSM

# Configuration

# Path to MusicSync Server database file
# Notice: DB file should be generated by MSS before running this script!
dbPath='msync.db'
# Path to audios dir
adir='audios'
# VK Auth token. Please get it from link below.
# https://oauth.vk.com/authorize?client_id=3697615&scope=audio,offline&response_type=token
token=''
# URL to reload API path
reloadUrl='http://localhost:8084/control/reload'
# token of user account, that have system control permissions at your MusicSync Server installation, grab it from browser cookies
msync_token=''

print('VK to MusicSync Audios Exporter by MelnikovSM')
import pickle, os, sys, vk, re, urllib, urllib2
from time import time

def saveDB(dbPath,db):
	output = open(dbPath, 'wb')
	pickle.dump(db, output)
	output.close()
def loadDB(dbPath):
	input = open(dbPath, 'rb')
	db = pickle.load(input)
	input.close()
	return db
def regAudio(lst, artist, title):
	try:
		lst.insert(0, {})
		lst[0]['filename']=str(int(time()*10000))
		lst[0]['artist']=artist
		lst[0]['title']=title
		return lst[0]['filename'], lst
	except: return False
def id2meta(audios, id):
	for audio in audios:
		if audio['id']==id:
			try:
					return audio['artist'], audio['title'], audio['url']
			except KeyError: return False, '', ''
	return False, '', ''

if os.path.isfile(dbPath):
	db=loadDB(dbPath)
	print('Logging in VK..')
	vkapi=vk.API(vk.Session(access_token=token), v='5.53', lang='ru', timeout=10)
	audios=vkapi.audio.get()['items']
	x=len(audios)
	print('Searching for not uploaded songs..')
	aids=[]
	if (not 'vkLastAID' in db['settings']):
		print('This first VKExport launch for all MusicSync DB time, creating DB config param settings\\vkLastAID..')
		db['settings']['vkLastAID']=0
	for audio in audios: 
		if audio['id']>db['settings']['vkLastAID']: aids.append(audio['id'])
	if len(aids)>0:
		print(str(len(aids))+' new audios found, downloading..')
		db['settings']['vkLastAID']=aids[(len(aids)-1)]
		aids.sort()
		n=1
		newa=[]
		for aid in aids:
			a,t,u=id2meta(audios, aid)
			sys.stdout.write('Processing audio "'+a+' - '+t+'" ('+str(n)+'/'+str(len(aids))+').. ')
			if not a==False:
				fname, newa = regAudio(newa, a,t)
				try:
					urllib.urlretrieve(u, os.path.join(adir, str(fname)))
					print('Pass')
				except: print('Failed')
			else: print('Failed')
			n+=1
		n+=1
		print('Complete! Saving DB & reloading server..')
		db=loadDB(dbPath)
		db['audios']=newa+db['audios']
		db['settings']['vkLastAID']=aids[(len(aids)-1)]
		saveDB(dbPath, db)
		try: urllib2.urlopen(urllib2.Request(url=reloadUrl,data=urllib.urlencode({'token': msync_token}))).read()
		except urllib2.HTTPError: print('Failed')
	else: print('No new audios uploaded yet, resting.')
else: print('Critical error: DB file not found.')
