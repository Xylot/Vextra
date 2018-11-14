import datetime
import json
import sys
import requests
import os
import time
import enum
import platform
import math
import ctypes.wintypes
from tqdm import tqdm
from stat import S_ISREG, ST_CTIME, ST_MODE

DELAY_AMOUNT = 10
UPLOAD_BATCH_COUNT = 15

class uploadState(enum.Enum):
	setup = 1
	openingFile = 2
	uploadingFile = 3
	interpretingReply = 4
	waitingForSuccessfulUpload = 5
	uploadSuccessful = 6
	uploadUnsuccessful = 7
	queueOverloadDelay = 8

class uploadStateDescriptions(enum.Enum):
	setup = 'Initializing'
	openingFile = 'Opening file'
	uploadingFile = 'Uploading file'
	interpretingReply = 'Interpreting reply'
	waitingForSuccessfulUpload = 'Waiting for replay to be parsed'
	uploadSuccessful = 'Replay successfully uploaded'
	uploadUnsuccessful = 'Replay was not uploaded successfully'
	queueOverloadDelay = 'Delaying the next upload to not overload the queue'

def getUserDemoPath(platform):
	if sys.argv[1]:
		return sys.argv[1]

	if platform == 'win':
		CSIDL_PERSONAL= 5
		SHGFP_TYPE_CURRENT= 0
		buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
		ctypes.windll.shell32.SHGetFolderPathW(0, CSIDL_PERSONAL, 0, SHGFP_TYPE_CURRENT, buf)
		dPath = str(buf.value) + '\\My Games\\Rocket League\\TAGame\\Demos\\'
		return dPath
	elif platform == 'mac':
		dPath = '~/Library/Application Support/Rocket League/TAGame/Demos'
		return dPath

def assignPathFromOperatingSystem():
	if platform.system() == 'Windows':
		return getUserDemoPath('win')
	elif platform.system() == 'Darwin':
		return getUserDemoPath('mac')

def clearScreen():
	os.system('cls' if os.name == 'nt' else 'clear')

demoPath = assignPathFromOperatingSystem()
uploadURL = 'https://calculated.gg/api/upload'
latestReplayName = ''

def updateCurrentState(state, status):
	sys.stdout.write('\r')
	sys.stdout.flush()
	if(state == uploadState.waitingForSuccessfulUpload):
		sys.stdout.write('Current state: ' + str(state.name) + '  Parse status: ' + status)
	else:
		sys.stdout.write('Current state: ' + str(state.name) + ' ' * 40)
	sys.stdout.flush()

def main():
	replayFileList = getReplayNames()
	replayCount = len(replayFileList)
	arguments = str(sys.argv)
	clearScreen()
	batchUpload(replayFileList, replayCount)
	print('Your replays have been successfully uploaded')

def batchUpload(replayFileList, replayCount):
	latestReplayName = ''
	openReplays = {}
	batchCount = 0
	numberOfBatches = math.ceil(replayCount / UPLOAD_BATCH_COUNT)
	for i in range(numberOfBatches):
		for j in range(UPLOAD_BATCH_COUNT):
			j = j + batchCount * 15
			openReplays.update ({
				'replays': open(replayFileList[j][0], 'rb')
			})
		print(openReplays)
		currentReplay = str(replayFileList[i][1])
		print('\nLatest Replay Uploaded: ' + latestReplayName)
		updateCurrentState(uploadState.openingFile, '')
		uploadReplay(uploadURL, openReplays)
		latestReplayName = currentReplay
		delayAfterUpload(DELAY_AMOUNT)
		clearScreen()
		batchCount = batchCount + 1
		

def singleUpload():
	for file in tqdm(replayFileList, desc='Upload progress: ', total=replayCount):
		openReplay = {
			'replays': open(file[0], 'rb')
		}
		currentReplay = str(file[1])
		print('\nLatest Replay Uploaded: ' + latestReplayName)
		updateCurrentState(uploadState.openingFile, '')
		uploadReplay(uploadURL, openReplay)
		latestReplayName = currentReplay
		delayAfterUpload(DELAY_AMOUNT)
		clearScreen()

def getReplayNames():
	data = (os.path.join(demoPath, fn) for fn in os.listdir(demoPath))
	data = ((os.stat(path), path) for path in data)

	data = ((stat[ST_CTIME], path)
				for stat, path in data if S_ISREG(stat[ST_MODE]))

	replayAttributes = []
	replayFilesAbsPaths = []
	replayFileNames = []

	for cdate, path in sorted(data):
		replayAttributes.append([os.path.abspath(path), os.path.basename(path)])

	for fileName in replayAttributes[0]:
		if ".replay" not in fileName:
			replayFilesAbsPaths.remove(fileName)

	for fileName in replayAttributes[1]:
		if ".replay" not in fileName:
			replayFilesAbsPaths.remove(fileName)

	return replayAttributes

def uploadReplay(uploadURL, replayFile):
	updateCurrentState(uploadState.uploadingFile, '')
	reply = requests.post(uploadURL, files = replayFile)

	updateCurrentState(uploadState.interpretingReply, '')
	if not list(reply.json()):
		message = 'No files uploaded, not a replay'
		updateCurrentState(uploadState.uploadUnsuccessful, '')

	if reply.status_code == 202:
		reply_id = list(reply.json())[0]
		payload = {
			'ids': reply_id
		}
		monitorUploadStatus(uploadURL, payload, 'SUCCESS')

	else :
		message = 'No files uploaded, error ' + reply.status_code
		updateCurrentState(uploadState.uploadUnsuccessful, '')

def monitorUploadStatus(uploadURL, payload, statusCode):
	while True:
		status = requests.get(uploadURL, params = payload)
		response = str(list(status.json())[0])
		if response == 'FAILURE':
			updateCurrentState(uploadState.uploadUnsuccessful, response)
			time.sleep(5)

		updateCurrentState(uploadState.waitingForSuccessfulUpload, response)
		if checkForResponse(response, 'SUCCESS', 3):
			updateCurrentState(uploadState.uploadSuccessful, '')
			break

def checkForResponse(status, waitCode, sleepAmount):
	if status == waitCode:
		return True
	else:
		time.sleep(sleepAmount)
		return False

def delayAfterUpload(delay):
	updateCurrentState(uploadState.queueOverloadDelay, '')
	time.sleep(delay)


if __name__ == '__main__':
	main()
