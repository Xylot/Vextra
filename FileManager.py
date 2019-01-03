import platform
import sys
try:
  import ctypes.wintypes
except:
  pass
import os
import math
import time
import pandas as pd
from multiprocessing.dummy import Pool as ThreadPool
from stat import S_ISREG, ST_CTIME, ST_MODE
from pprint import pprint
from tqdm import tqdm
from DatabaseManager import DatabaseManager

# Gets and organizes information from the user's demo path 
class FileManager:

	# Takes in three optional user-specified arguments:
	#	Demo path
	#	Database path
	#	Intent to create database
	# These options overwrite their respecitve defualt values
	# Also defines how many replays will be uploaded at a time with the batchAmount parameter
	def __init__(self, args=[None, None, None], batchAmount=15):
		self.setAttributes(args, batchAmount)

	# Runs the getter functions in the class and stores them
	def setAttributes(self, args, batchAmount):
		self.replayPath = self.getUserDemoPath(args[0])
		self.replayList = self.getReplayList()
		self.replayCount = self.getReplayCount()
		self.replayFolderName = self.getReplayFolderName()
		self.batchAmount = batchAmount
		self.batchCount = self.getBatchCount()
		self.replayBatches = self.seperateBatches()
		self.databaseManager = DatabaseManager()
		self.replayDatabase = self.importReplayDatabase(args[1])
		self.createDatabase = args[2]
		if self.replayCount < self.batchAmount:
			self.singleBatch = True
		else:
			self.singleBatch = False	

	# Returns the complete list of properties derived from the user's demo path
	def getAttributes(self):
		return [self.replayPath, self.replayList, self.replayCount,
				self.replayFolderName, self.replayBatches, self.batchAmount, 
				self.batchCount, self.singleBatch, self.replayDatabase, self.createDatabase]

	# Finds the path Rocket League uses to store the replay files on the system
	# Default windows path:
	# Default macos path: 
	def getUserDemoPath(self, userDefinedPath=None):
		if userDefinedPath != None:
			return userDefinedPath

		if platform.system() == 'Windows':
			CSIDL_PERSONAL= 5
			SHGFP_TYPE_CURRENT= 0
			buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
			ctypes.windll.shell32.SHGetFolderPathW(0, CSIDL_PERSONAL, 0, SHGFP_TYPE_CURRENT, buf)
			dPath = str(buf.value) + '\\My Games\\Rocket League\\TAGame\\Demos'
			return dPath
		elif platform.system() == 'Darwin':
			dPath = '/Library/Application Support/Rocket League/TAGame/Demos'
			#dPath = '/Users/Joseph/Documents/GitHub/Vextra/Resources/Replays/Set of 20'
			return dPath	

	# Gets the folder name that the replay files are stored in
	# Can be used for replay grouping
	def getReplayFolderName(self):
		self.databasePath = os.path.basename(self.replayList[0][1])
		#self.databasePath = defaultDatabasePath

	# Defines how many batches of files will be uploaded
	# This is calculated based on the total number of replays and the batch amount
	def getBatchCount(self):
		return math.ceil(self.replayCount / self.batchAmount)

	# Creates a list of the files in the demo path and sorts them by date
	# The list is created in the format:
	#	[Full replay path, replay filename, '']
	def getReplayList(self):
		data = (os.path.join(self.replayPath, fn) for fn in os.listdir(self.replayPath))
		data = ((os.stat(path), path) for path in data)

		data = ((stat[ST_CTIME], path)
					for stat, path in data if S_ISREG(stat[ST_MODE]))

		replayAttributes = []

		for cdate, path in sorted(data):
			if ".replay" in path:
				replayAttributes.append([os.path.abspath(path), os.path.basename(path), ''])

		return replayAttributes

	# Gets the total amount of replays in the folder
	# This is used to calculate the batch count
	def getReplayCount(self):
		return len(self.replayList)

	# Gets the name of a replay file without the file extension
	def getReplayName(self, replayFileName):
		return replayFileName.replace('.replay', '')

	# Seperates the list of replays into even batches specified by the batchAmount parameter
	def seperateBatches(self):
		if len(self.replayList) < self.batchAmount:
			self.oneBatch = True
			return [self.replayList]
		else:
			self.oneBatch = False
			return [self.replayList[i:i + self.batchAmount] for i in range(0, len(self.replayList), self.batchAmount)]

	# Imports a pre-created csv database containing the guid, path and name of replay files on the system
	# This database allows the user to skip parsing the replay files for information directly
	# This can be provide a significant increase in completion time for the upload
	def importReplayDatabase(self, userDefinedDatabase=None):
		try:
			if userDefinedDatabase is None:
				self.importedDatabase = self.databaseManager.createEmptyDataframe()
				#self.importedDatabase = self.databaseManager.read('ReplayDB.csv')
			else:
				if os.path.isfile(userDefinedDatabase):
					self.importedDatabase = self.databaseManager.read(userDefinedDatabase)
				else:
					self.importedDatabase = self.databaseManager.createEmptyDataframe()
			return self.importedDatabase
		except Exception as e:
			return self.databaseManager.createEmptyDataframe()


	


