import datetime
import json
import sys
import requests
import os
import time
from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
    AdaptiveETA, FileTransferSpeed, FormatLabel, Percentage, \
    ProgressBar, ReverseBar, RotatingMarker, \
    SimpleProgress, Timer, UnknownLength

pbar = ProgressBar()

def main():
	replay_file_path = "C:/Users/Joseph/Documents/My Games/Rocket League/TAGame/Demos/7FE4E971472B39F07165C095836F7430.replay"
	uploadURL = 'https://calculated.gg/api/upload'
	replays = {}
	uploadCount = 0
	replayFileList = getReplayNames()
	replayCount = len(replayFileList)

	widgets = ['Test: ', Percentage(), ' ', Bar(marker=RotatingMarker()),' ', ETA(), ' ', FileTransferSpeed()]
	pbar = ProgressBar(widgets=widgets, maxval=replayCount).start()

	#for file in pbar((file for file in range(5))):
	for file in pbar(replayFileList):
		print(file)
		openReplay = {
			'replays': open(file, 'rb')
		}
		#print('uploading...')
		uploadReplay(uploadURL, openReplay)
		uploadCount = uploadCount + 1
		print("Replays uploaded: " + str(uploadCount) + "  Latest replay: " + x)
		time.sleep(2)

def getReplayNames():
	demoPath = "C:/Users/Joseph/Documents/My Games/Rocket League/TAGame/Demos/"
	fileList = [(x[0], time.ctime(x[1].st_ctime)) for x in sorted([(fn, os.stat(fn)) for fn in os.listdir(demoPath)], key = lambda x: x[1].st_ctime)]
	timeList = []

	for x in fileList:
		if "2018" in x[1]:
			timeList.append(x[0])# print(list(reversed(timeList)))

	timeListReverse = list(reversed(timeList))# print(onlyfiles)

	for x in timeListReverse:
		if ".replay" not in x:
			timeListReverse.remove(x)

	return timeListReverse

def uploadReplay(uploadURL, replayFile):
	print('uploading...')
	reply = requests.post(uploadURL, files = replayFile)
	print(reply)
	print('received reply...')


	if not list(reply.json()):
		message = 'No files uploaded, not a replay'

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

def monitorUploadStatus(uploadURL, payload, statusCode):
	while True:		
		status = requests.get(uploadURL, params = payload)
		response = list(status.json())[0]
		if checkForResponse(response, 'SUCCESS', 1):
			print('replay uploaded!')
			break

def checkForResponse(status, waitCode, sleepAmount):
	if status is not waitCode:
		time.sleep(sleepAmount)
		return False
	else:
		return True



if __name__ == '__main__':
	main()