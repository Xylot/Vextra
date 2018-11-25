import datetime
import json
import sys
import requests
import os
import time
import enum
import platform
import math
import carball
import csv
import pandas as pd
from carball.json_parser.game import Game
import ctypes.wintypes
from tqdm import tqdm
from stat import S_ISREG, ST_CTIME, ST_MODE

DELAY_AMOUNT = 60
UPLOAD_BATCH_COUNT = 15
LOGGING = True

class UpdateStatus:
	
	def __init__(self):
		self.status = self.UploadState
		self.previousState = self.status.setup

	class UploadState(enum.Enum):
		setup = 1
		openingFile = 2
		openingBatch = 3
		uploadingFile = 4
		uploadingBatch = 5
		interpretingReply = 6
		interpretingReplies = 7
		waitingForSuccessfulUpload = 8
		uploadSuccessful = 9
		uploadUnsuccessful = 10
		queueOverloadDelay = 11
		uploadTimeout = 12

	class UploadStateDescriptions(enum.Enum):
		setup = 'Initializing'
		openingFile = 'Opening file'
		openingBatch = 'Opening the batch of files'
		uploadingFile = 'Uploading file'
		uploadingBatch = 'Uploading the batch of files'
		interpretingReply = 'Interpreting reply'
		interpretingReplies = 'Interpeties replies of the batch upload'
		waitingForSuccessfulUpload = 'Waiting for replay to be parsed'
		uploadSuccessful = 'Replay successfully uploaded'
		uploadUnsuccessful = 'Replay was not uploaded successfully'
		queueOverloadDelay = 'Delaying the next upload to not overload the queue'
		uploadTimeout = 'Replay parsing has taken too long'

	def clearScreen(self):
		os.system('cls' if os.name == 'nt' else 'clear')

	def update(self, state, status):
		if not LOGGING:
			return

		sys.stdout.write('\r')
		sys.stdout.flush()

		if state != self.previousState:
			sys.stdout.write('Current state: ' + str(state.name) + ' ' * 40)

		self.previousState = state
		sys.stdout.flush()

class Replays:
	
	def __init__(self):
		self.replayPath = self.assignPathFromOperatingSystem()
		self.replayFileList = self.getReplayNames(self.replayPath)
		self.csvArray = self.generateArrayFromCSV()	

	def getUserDemoPath(self, platform):
		if len(sys.argv) > 2:
			return sys.argv[1]

		if platform == 'win':
			CSIDL_PERSONAL= 5
			SHGFP_TYPE_CURRENT= 0
			buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
			ctypes.windll.shell32.SHGetFolderPathW(0, CSIDL_PERSONAL, 0, SHGFP_TYPE_CURRENT, buf)
			dPath = str(buf.value) + '\\My Games\\Rocket League\\TAGame\\Demos\\'
			return dPath
		elif platform == 'mac':
			#dPath = '~/Library/Application Support/Rocket League/TAGame/Demos'
			dPath = '/Users/Joseph/Documents/GitHub/CalculatedGG-Uploader/Test Files/Replays'
			return dPath

	def assignPathFromOperatingSystem(self):
		if platform.system() == 'Windows':
			import ctypes.wintypes
			return self.getUserDemoPath('win')
		elif platform.system() == 'Darwin':
			return self.getUserDemoPath('mac')

	def getReplayNames(self, demoPath):
		data = (os.path.join(demoPath, fn) for fn in os.listdir(demoPath))
		data = ((os.stat(path), path) for path in data)

		data = ((stat[ST_CTIME], path)
					for stat, path in data if S_ISREG(stat[ST_MODE]))

		replayAttributes = []

		for cdate, path in sorted(data):
			replayAttributes.append([os.path.abspath(path), os.path.basename(path)])

		for fileName in replayAttributes[0]:
			if ".replay" not in fileName:
				replayFilesAbsPaths.remove(fileName)

		for fileName in replayAttributes[1]:
			if ".replay" not in fileName:
				replayFilesAbsPaths.remove(fileName)

		return replayAttributes

	def generateGUIDcsv(self):
		with open('ReplayGuidsTest1.csv', 'a') as csvfile:
			filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
			filewriter.writerow(['Replay Name', 'Replay GUID', 'Replay Path', 'JSON Path'])
			for i in range(len(self.replayFileList)):
				if not self.checkForPreviousDecompile(self.replayFileList[i][1]):
					try:
						decompiler = DecompileReplay(self.replayFileList[i])
						row = [decompiler.replayName, decompiler.getReplayGUID(), decompiler.replayPath, decompiler.replayPathJson]
						filewriter.writerow(row)
						print('Wrote to file: ' + str(row))
						os.remove(decompiler.replayPathJson)
						print('Deleted json: ' + decompiler.replayPathJson)
					except:
						print('Unable to decompile: ' + self.replayFileList[i][1])
				else:
					print('Replay ' + self.replayFileList[i][1] + ' has already been decompilied')

	def generateArrayFromCSV(self):
		results = []
		with open("ReplayGuidsTest1.csv") as csvfile:
			reader = csv.reader(csvfile, delimiter=',', quotechar='|')
			for row in reader:
				results.append(row)
		return results

	def removeEmptyRows(self):
		df = pd.read_csv('ReplayGuidsTest.csv')
		df.to_csv('ReplayGuidsTest1.csv', index=False)

	def checkForPreviousDecompile(self, replayName):
		for i in range(len(self.csvArray)):
			if replayName in self.csvArray[i]:
				print(self.csvArray[i])
				return True
		return False

class BatchUpload:
	
	def __init__(self, replayList, batchAmount):
		self.replayList = replayList
		self.batchAmount = batchAmount
		self.replayCount = self.getReplayCount()
		self.batchCount = self.getBatchCount()
		self.replayBatches = self.seperateBatches()
		self.statusUpdater = UpdateStatus()
		self.uploadURL = 'https://calculated.gg/api/upload'
		self.statusUpdater.clearScreen()
		#self.g = self.getBatchGUIDs(self.replayBatches[0])

	def getReplayCount(self):
		return len(self.replayList)

	def getBatchCount(self):
		return math.ceil(self.replayCount / self.batchAmount)

	def seperateBatches(self):
		batches = []
		currentBatchList = []
		for i in range(self.batchCount):
			for j in range(self.batchAmount):
				try:
					currentBatchList.append(self.replayList[i * 15 + j])
				except:
					pass
			batches.append(currentBatchList[0:15])
			currentBatchList.clear()

		return batches

	def getBatchGUIDs(self, batch):
		guidList = []
		for i in range(len(batch)):
			decompiler = DecompileReplay(batch[i])
			guid = decompiler.getReplayGUID()
			guidList.append(guid)
		print(guidList)

	def upload(self):
		for i in tqdm(range(self.batchCount), desc='Upload progress: ', position=0):
			statusPayloads = []
			for j in tqdm(range(self.batchAmount), desc='	Batch upload progress: ', ncols=100, position=1):
				#self.statusUpdater.update(self.statusUpdater.UploadState.uploadingBatch, '')
				openReplay = {
					'replays': open(self.replayBatches[i][j][0], 'rb')
				}
				reply = self.getUploadReply(openReplay)
				statusPayloads.append(self.getReplayPayload(reply, self.replayBatches[i][j][1]))
			self.monitorBatchStatus(statusPayloads)
			self.delayAfterUpload(DELAY_AMOUNT)
			self.statusUpdater.clearScreen()

	def getUploadReply(self, replayFile):
		return requests.post(self.uploadURL, files = replayFile)

	def getReplayPayload(self, reply, replayName):
		if reply.status_code == 202:
			reply_id = list(reply.json())[0]
			payload = {
				'ids': reply_id
			}
			fullPayload = [replayName, payload]
			print(fullPayload)
			return fullPayload

	def monitorBatchStatus(self, payloads):
		self.statusUpdater.update(self.statusUpdater.UploadState.waitingForSuccessfulUpload, '')
		startTime = time.time()
		while True:
			uploadStatus = self.getUploadBatchStatus(payloads)
			if self.checkForBatchResponse(uploadStatus, 'SUCCESS'):
				self.statusUpdater.update(self.statusUpdater.UploadState.uploadSuccessful, '')
				break
			if self.checkForTimeout(startTime):
				self.statusUpdater.update(self.statusUpdater.UploadState.uploadTimeout, '')
				break
			time.sleep(10)

	def getUploadBatchStatus(self, statusPayloads):
		statusList = []
		for i in range(self.batchAmount):
			status = requests.get(self.uploadURL, params = statusPayloads[i][1])
			response = str(list(status.json())[0])
			statusList.append([statusPayloads[i][0], response])
		return statusList

	def checkForBatchResponse(self, uploadResponses, waitCode):
		for i in range(self.batchAmount):
			if uploadResponses[i][1] != waitCode:
				return False
		return True

	def delayAfterUpload(self, delay):
		self.statusUpdater.update(self.statusUpdater.UploadState.queueOverloadDelay, '')
		time.sleep(delay)

	def checkForTimeout(self, oldEpoch):
		return time.time() - oldEpoch >= 60

class SingleUpload:
	
	def __init__(self, replay):
		self.replay = replay
		self.uploadURL = 'https://calculated.gg/api/upload'
		self.statusUpdater = UpdateStatus()
		self.statusUpdater.clearScreen()

	def upload(self):
		for i in tqdm(range(1), desc='Upload progress: '):
			openReplay = {
				'replays': open(self.replay, 'rb')
			}
			uploadReplay(self.uploadURL, openReplay)
		
		print('\nReplay Uploaded: ' + self.replay)

	def uploadReplay(self, replayFile):
		self.statusUpdater.update(self.statusUpdater.UploadState.uploadingFile, '')
		reply = requests.post(self.uploadURL, files = replayFile)

		self.statusUpdater.update(self.statusUpdater.UploadState.interpretingReply, '')
		if not list(reply.json()):
			message = 'No files uploaded, not a replay'
			self.statusUpdater.update(self.statusUpdater.UploadState.uploadUnsuccessful, '')

		if reply.status_code == 202:
			reply_id = list(reply.json())[0]
			payload = {
				'ids': reply_id
			}
			monitorUploadStatus(self.uploadURL, payload, 'SUCCESS')

		else :
			message = 'No files uploaded, error ' + reply.status_code
			self.statusUpdater.update(self.statusUpdater.UploadState.uploadUnsuccessful, '')

	def monitorUploadStatus(self, payload, statusCode):
		while True:
			status = requests.get(self.uploadURL, params = payload)
			response = str(list(status.json())[0])
			if response == 'FAILURE':
				self.statusUpdater.update(self.statusUpdater.UploadState.uploadUnsuccessful, '')
				time.sleep(5)

			self.statusUpdater.update(self.statusUpdater.UploadState.waitingForSuccessfulUpload, '')
			if checkForResponse(response, 'SUCCESS', 3):
				self.statusUpdater.update(self.statusUpdater.UploadState.uploadSuccessful, '')
				break

	def checkForResponse(self, status, waitCode, sleepAmount):
		if status == waitCode:
			return True
		else:
			time.sleep(sleepAmount)
			return False

class DecompileReplay:

	def __init__(self, replay):
		self.replayPath = replay[0]
		self.replayName = replay[1]
		self.replayPathJson = self.getReplayJson()		

	def getReplayJson(self):
		replayJson = self.replayPath.replace('.replay', '.json')
		replayJson = replayJson.replace('/Replays', '/Decompiled Replays/')
		return replayJson

	def getReplayGUID(self):
		startTime = time.time()
		_json = carball.decompile_replay(self.replayPath, self.replayPathJson, overwrite=True)
		decTime = time.time() - startTime
		print('Decompile time: ' + str(decTime))
		game = Game()
		game.initialize(loaded_json=_json)
		return game.game_info.match_guid

def main():
	replays = Replays()
	#replays.generateGUIDcsv()
	batchUploader = BatchUpload(replays.replayFileList, UPLOAD_BATCH_COUNT)
	batchUploader.upload()
	print('Your replays have been successfully uploaded')

if __name__ == '__main__':
	main()
