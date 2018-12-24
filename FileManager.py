import platform
import sys
import ctypes.wintypes
import os
import math
import time
import pandas as pd
from multiprocessing.dummy import Pool as ThreadPool
from stat import S_ISREG, ST_CTIME, ST_MODE
from pprint import pprint
from tqdm import tqdm
from DatabaseManager import DatabaseManager


class FileManager:

	def __init__(self, args, batchAmount=15):
		self.setAttributes(args, batchAmount)

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

	def getAttributes(self):
		return [self.replayPath, self.replayList, self.replayCount,
				self.replayFolderName, self.replayBatches, self.batchAmount, 
				self.batchCount, self.singleBatch, self.replayDatabase, self.createDatabase]

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
			#dPath = '~/Library/Application Support/Rocket League/TAGame/Demos'
			dPath = '/Users/Joseph/Documents/GitHub/CalculatedGG-Uploader/Test Files/Replays'
			return dPath	

	def getReplayFolderName(self):
		self.databasePath = os.path.basename(self.replayList[0][1])
		#self.databasePath = defaultDatabasePath

	def getBatchCount(self):
		return math.ceil(self.replayCount / self.batchAmount)

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

	def getReplayCount(self):
		return len(self.replayList)

	def getReplayName(self, replayFileName):
		return replayFileName.replace('.replay', '')

	def seperateBatches(self):
		if len(self.replayList) < self.batchAmount:
			self.oneBatch = True
			return [self.replayList]
		else:
			self.oneBatch = False
			return [self.replayList[i:i + self.batchAmount] for i in range(0, len(self.replayList), self.batchAmount)]

	def importReplayDatabase(self, userDefinedDatabase=None):
		try:
			if userDefinedDatabase is None:
				self.importedDatabase = self.databaseManager.read('ReplayDB.csv')
			else:
				if os.path.isfile(userDefinedDatabase):
					self.importedDatabase = self.databaseManager.read(userDefinedDatabase)
				else:
					self.importedDatabase = self.databaseManager.createEmptyDataframe()
			return self.importedDatabase
		except Exception as e:
			return self.databaseManager.createEmptyDataframe()


	


