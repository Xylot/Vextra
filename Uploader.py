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

# Uploads the files to the server using the attributes returned from the file manager
class Uploader:
	
	# Specifies the endpoints for the file uploads and replay data retriever
	uploadURL = 'https://calculated.gg/api/upload'
	replayURL = 'https://calculated.gg/api/replay/'
	
	# Takes in the attributes from the file manager object
	# Also instantiates:
	# 	The status manager to continuously clean up the output interface
	#	The database manager to interface with the local replay database
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

	# Uploads the replay files in batches:
	# The uploader uses a progress bar to provide the user with the progress of the full upload
	# Before uploading, the server is queried with the replay's unique identifier to ensure that it will not be a duplicate upload
	# Once the batch is fully uploaded to the server, its parse status is continuously monitored
	# After 60 seconds have passed or the batch has been fully parsed by the server, the next batch is uploaded
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

	# Uploads a replay to the server
	# Before the upload, the replay's unique identifier is retrieved and used to check for a duplicate upload
	# The post request's reply is stored and added to the status list of the batch for use by the status monitor
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

	# Queries the server for the replay's unique identifier
	# If the replay already exists on the server, the response will contain data from the replay
	# If the replay was not found on the server, the response will contain the word message
	def checkForDuplicateUpload(self, replayGUID):
		status = requests.get(self.replayURL + replayGUID)
		response = list(status.json())
		if 'message' in response:
			return False
		return True

	# Sends the file to the server and returns the server's reply
	# The post request is sent using the upload endpoint as well as the opened file from the postReplay function
	def getUploadReply(self, replayFile):
		return requests.post(self.uploadURL, files = replayFile)

	# Uses the status code returned from the getUploadReply function to get the id of the replay stored on the server
	# This id is used by the status monitor to query for the parse status without having the upload the file again
	def getReplayPayload(self, reply, replayName):
		if reply.status_code == 202:
			reply_id = list(reply.json())[0]
			payload = {
				'ids': reply_id
			}
			fullPayload = [replayName, payload]
			return fullPayload

	# Status monitor for the parse status of a batch
	# Takes in the payload list, containing the replay ids, of the uploaded files
	# Checks for parse status for 60 seconds or until every replay returns a success or fail
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

	# Queries the server for the parse status of every replay in the current batch
	# The status of the batch is stored in a list with each element in the format:
	#	[Replay name, Status code]
	def getUploadBatchStatus(self, statusPayloads):
		statusList = []
		for payload in statusPayloads:
			status = requests.get(self.uploadURL, params = payload[1])
			response = str(list(status.json())[0])
			statusList.append([payload[0], response])
		return statusList

	# Checks for a specific response for each replay in the current batch
	# This response is usually a SUCCESS code but can also a fail or pending
	def checkForBatchResponse(self, uploadResponses, waitCode):
		for i in range(self.batchAmount):
			if uploadResponses[i][1] != waitCode:
				return False
		return True

	# Delays the program a user-specified amount of time after the batch is uploaded
	# This delay is used to prevent overwhelming the server as well as give other users a chance to have their replays uploaded
	def delayAfterUpload(self, delay):
		self.statusUpdater.update(self.statusUpdater.UploadState.queueOverloadDelay, '')
		time.sleep(delay)

	# Checks if a user-specified amount of time has passed since a time value was stored
	# This is primarily used by the status monitor to indicate that the upload is taking too long
	def checkForTimeout(self, oldEpoch, length):
		return time.time() - oldEpoch >= length

	# Gets the unique identifier of a replay file for use by the checkForDuplicateUpload function
	# If the user has a pre-created database, the unique identifier is retrieved from it
	# If no database is being used, the unique identifer is retrieved using the boxcars parser 
	def getGUID(self, replay, database=None):
		if database is None: database = self.replayDatabase
		row = self.databaseManager.getRow(value=replay[1], database=database)
		if row is None:

			try: return ReplayDatabaseManager([None] * 9).getReplayGUID(replay[0], 'boxcars')
			except: return None

		else: return str(row.iloc[0]['GUID'])
	
	# Creates a database if the user specified to do so in an argument on the initial program run
	# The database is created in csv format with the row format of:
	#	Replay name, Replay GUID, Full replay path	
	def createDatabase(self):
		if self.attributes[9] == True:
			self.statusUpdater.clearScreen()
			ReplayDatabaseManager(self.attributes).exportReplayDatabase()
			print('\n\nThe replay database has been created!')
			sys.exit()
		else:
			self.replayDatabase = self.attributes[8]
			self.databaseManager.database = self.replayDatabase
