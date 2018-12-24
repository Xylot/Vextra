import requests
import time
import enum
import json
import sys
from tqdm import tqdm
from pprint import pprint
from StatusUpdater import StatusUpdater
from DatabaseManager import DatabaseManager
from ReplayDatabaseManager import ReplayDatabaseManager

DELAY_AMOUNT = 30

class Uploader:
	
	uploadURL = 'https://calculated.gg/api/upload'
	replayURL = 'https://calculated.gg/api/replay/'
	
	def __init__(self, attributes):
		self.attributes = attributes
		self.replayList = attributes[1]
		self.replayCount = attributes[2]
		self.replayBatches = attributes[4]
		self.batchAmount = attributes[5]
		self.batchCount = attributes[6]
		self.databaseManager = DatabaseManager()
		self.statusUpdater = StatusUpdater()
		self.replayDatabase = self.createDatabase()		
		self.statusUpdater.clearScreen()

	def upload(self):
		for batch in tqdm(self.replayBatches, desc='Upload progress: ', position=0):
			self.statusPayloads = []
			self.previouslyUploaded = []
			for replay in tqdm(batch, desc='	Batch upload progress: ', ncols=100, position=1):
				
				try: self.postReplay(replay)					
				except Exception as e: continue
			
			try: self.monitorBatchStatus(self.statusPayloads)				
			except Exception as e: continue

		print('\n\nAll files have been successfully uploaded!')

	def postReplay(self, replay):
		currentGUID = self.getGUID(replay, self.replayDatabase)
		if currentGUID is not None:
			if self.checkForDuplicateUpload(currentGUID):
				self.previouslyUploaded.append(True)
				return
		openReplay = {
			'replays': open(replay[0], 'rb')
		}
		reply = self.getUploadReply(openReplay)
		self.statusPayloads.append(self.getReplayPayload(reply, replay[1]))

	def checkForDuplicateUpload(self, replayGUID):
		status = requests.get(self.replayURL + replayGUID)
		response = list(status.json())
		if 'message' in response:
			return False
		return True

	def getUploadReply(self, replayFile):
		return requests.post(self.uploadURL, files = replayFile)

	def getReplayPayload(self, reply, replayName):
		if reply.status_code == 202:
			reply_id = list(reply.json())[0]
			payload = {
				'ids': reply_id
			}
			fullPayload = [replayName, payload]
			return fullPayload

	def monitorBatchStatus(self, payloads, startTime=time.time()):
		if not any(payloads) or all(True for duplicate in self.previouslyUploaded):
			self.statusUpdater.clearScreen()
			return
		self.statusUpdater.update(self.statusUpdater.UploadState.waitingForSuccessfulUpload, '')
		while True:
			uploadStatus = self.getUploadBatchStatus(payloads)
			if self.checkForBatchResponse(uploadStatus, 'SUCCESS'):
				self.statusUpdater.update(self.statusUpdater.UploadState.uploadSuccessful, '')
				break
			if self.checkForTimeout(startTime, 10):
				self.statusUpdater.update(self.statusUpdater.UploadState.uploadTimeout, '')
				break
			time.sleep(5)

		self.delayAfterUpload(DELAY_AMOUNT)
		self.statusUpdater.clearScreen()

	def getUploadBatchStatus(self, statusPayloads):
		statusList = []
		for payload in statusPayloads:
			status = requests.get(self.uploadURL, params = payload[1])
			response = str(list(status.json())[0])
			statusList.append([payload[0], response])
		return statusList

	def checkForBatchResponse(self, uploadResponses, waitCode):
		for i in range(self.batchAmount):
			if uploadResponses[i][1] != waitCode:
				return False
		return True

	def delayAfterUpload(self, delay):
		self.statusUpdater.update(self.statusUpdater.UploadState.queueOverloadDelay, '')
		time.sleep(delay)

	def checkForTimeout(self, oldEpoch, length):
		return time.time() - oldEpoch >= length

	def getGUID(self, replay, database=None):
		if database is None: database = self.replayDatabase
		row = self.databaseManager.getRow(value=replay[1], database=database)
		if row is None:

			try: return ReplayDatabaseManager([None] * 9).getReplayGUID(replay[0], 'boxcars')
			except: return None

		else: return str(row.iloc[0]['GUID'])
			
	def createDatabase(self):
		if self.attributes[9] == True:
			self.statusUpdater.clearScreen()
			ReplayDatabaseManager(self.attributes).exportReplayDatabase()
			print('\n\nThe replay database has been created!')
			sys.exit()
		else:
			self.replayDatabase = self.attributes[8]
			self.databaseManager.database = self.replayDatabase
