import datetime
import json
import sys
import requests
import os
import time
import enum
from stat import S_ISREG, ST_CTIME, ST_MODE
from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
    AdaptiveETA, FileTransferSpeed, FormatLabel, Percentage, \
    ProgressBar, ReverseBar, RotatingMarker, \
    SimpleProgress, Timer, UnknownLength

demoPath = "C:/Users/Joseph/Documents/My Games/Rocket League/TAGame/Demos/"
uploadURL = 'https://calculated.gg/api/upload'
latestReplayName = ''


class uploadState(enum.Enum):
	setup = 1
	openingFile = 2
	uploadingFile = 3
	interpretingReply = 4
	waitingForSuccessfulUpload = 5
	uploadSuccessful = 6
	uploadUnsuccessful = 7

class uploadStateDescriptions(enum.Enum):
	setup = 'Initializing'
	openingFile = 'Opening file'
	uploadingFile = 'Uploading file'
	interpretingReply = 'Interpreting reply'
	waitingForSuccessfulUpload = 'Waiting for replay to be parsed'
	uploadSuccessful = 'Replay successfully uploaded'
	uploadUnsuccessful = 'Replay was not uploaded successfully'

currentState = uploadState.setup

def main():
	currentState = uploadState.setup
	replayFileList = getReplayNames()
	replayCount = len(replayFileList)
	latestReplayName = replayFileList[0][1]
	uploadCount = 0

	os.system('cls')
	pbar = setupProgressBar(6)	

	#for file in pbar((file for file in range(5))):
	for file in replayFileList[0:5]:
	#for file in replayFileList:
		#print(file)
		currentState = uploadState.openingFile
		printCurrentState()
		openReplay = {
			'replays': open(file[0], 'rb')
		}
		latestReplayName = str(file[1])
		uploadReplay(uploadURL, openReplay)
		uploadCount = uploadCount + 1
		os.system('cls')
		pbar.update(uploadCount)
		print('\nLatest Replay Uploaded: ' + latestReplayName)
		time.sleep(2)

def setupProgressBar(replayCount):
	widgets = ['Upload Progress: ', Percentage(), ' ', Bar(marker=RotatingMarker()),' ', ETA(), ' ', Counter(), '\nLatest Replay: ', latestReplayName]
	return ProgressBar(widgets=widgets, maxval=replayCount).start()

def getLatestReplay():
	return latestReplayName

def getReplayNames():
	#Relative or absolute path to the directory
	dir_path = demoPath

	#all entries in the directory w/ stats
	data = (os.path.join(dir_path, fn) for fn in os.listdir(dir_path))
	data = ((os.stat(path), path) for path in data)

	# regular files, insert creation date
	data = ((stat[ST_CTIME], path)
				for stat, path in data if S_ISREG(stat[ST_MODE]))

	replayAttributes = []
	replayFilesAbsPaths = []
	replayFileNames = []

	for cdate, path in sorted(data):
		#print(os.path.basename(path))
		#print(time.ctime(cdate), os.path.basename(path))
		replayFilesAbsPaths.append(os.path.abspath(path))
		replayFileNames.append(os.path.basename(path))
		replayAttributes.append([os.path.abspath(path), os.path.basename(path)])

	for fileName in replayAttributes[0]:
		if ".replay" not in fileName:
			replayFilesAbsPaths.remove(fileName)

	for fileName in replayAttributes[1]:
		if ".replay" not in fileName:
			replayFilesAbsPaths.remove(fileName)

	return replayAttributes

	# for x in fileList:
	# 	if "2018" in x[1]:
	# 		timeList.append(x[0])# print(list(reversed(timeList)))

	# timeListReverse = list(reversed(timeList))# print(onlyfiles)

	# for x in timeListReverse:
	# 	if ".replay" not in x:
	# 		timeListReverse.remove(x)

	# return timeListReverse

def printCurrentState():
	print('\rCurrent Status: ' + str(currentState))

def uploadReplay(uploadURL, replayFile):
	#print('uploading...')
	currentState = uploadState.uploadingFile
	printCurrentState()
	reply = requests.post(uploadURL, files = replayFile)

	currentState = uploadState.interpretingReply
	if not list(reply.json()):
		message = 'No files uploaded, not a replay'
		currentState = uploadState.uploadUnsuccessful
		printCurrentState()

	#if '202' in str(list(reply.json())[0]):
	if reply.status_code == 202:
		reply_id = list(reply.json())[0]
		payload = {
			'ids': reply_id
		}
		monitorUploadStatus(uploadURL, payload, 'SUCCESS')
		# status = requests.get(up_url, params = payload)
		# if list(status.json())[0] == 'FAILURE':
		# 	message = 'No files uploaded: FAILURE'

		# elif list(status.json())[0] in ['PENDING', 'STARTED', 'SUCCESS']:
		# 	message = 'replays have been queued for parsing'
		# 	waitForSuccess(status)# print(message)
		# else :
		# 	message = "Unknown status: " + list(status.json())[0]

	else :
		message = 'No files uploaded, error ' + reply.status_code
		currentState = uploadState.uploadUnsuccessful
		printCurrentState()

def monitorUploadStatus(uploadURL, payload, statusCode):
	currentState = uploadState.waitingForSuccessfulUpload
	printCurrentState()
	while True:		
		status = requests.get(uploadURL, params = payload)
		response = str(list(status.json())[0])
		if checkForResponse(response, 'SUCCESS', 1):
			currentState = uploadState.uploadSuccessful
			printCurrentState()
			break

def checkForResponse(status, waitCode, sleepAmount):
	if status == waitCode:
		return True
	else:
		time.sleep(5)
		return False

if __name__ == '__main__':
	main()