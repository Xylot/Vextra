import enum
import os
import sys

class StatusUpdater:
	
	def __init__(self):
		self.status = self.UploadState
		self.previousState = self.status.setup
		self.LOGGING = False
		self.clear = True

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
		if self.clear:
			os.system('cls' if os.name == 'nt' else 'clear')

	def update(self, state, status):
		if not self.LOGGING:
			return

		sys.stdout.write('\n\n\r')
		sys.stdout.flush()

		if state != self.previousState:
			sys.stdout.write('Current state: ' + str(state.name) + ' ' * 40)

		self.previousState = state
		sys.stdout.flush()