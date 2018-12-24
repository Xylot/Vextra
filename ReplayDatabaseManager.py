from Parser import Decompiler, Parser
from DatabaseManager import DatabaseManager
from pprint import pprint
from tqdm import tqdm

class ReplayDatabaseManager:

	defaultDatabasePath = 'ReplayDB.csv'
	defaultDatabaseHeader = [ 'Path', 'Name', 'GUID']

	def __init__(self, attributes):
		self.databaseManager = DatabaseManager()
		self.demoPathAttributes = attributes
		self.setAttributes()
		
	def setAttributes(self):
		self.replayList = self.demoPathAttributes[1]
		self.replayBatches = self.demoPathAttributes[4]
		self.singleBatch = self.demoPathAttributes[7]

	def getReplayGUID(self, replay, parser):
		try:
			jsonObject = Decompiler(replay).decompile(parser=parser, logTime=False)
			guid = Parser(jsonObject, parser).getGUID()
			if any(guid): return guid 
			else: return 'None'
		except:
			return 'Error'

	def getBatchGUIDs(self, batch):
		for replay in batch:
			replay[2] = self.getReplayGUID(replay[0], 'boxcars')
		return batch

	def printAllGUIDs(self):
		for batch in self.replayBatches:
			for replay in batch:
				print("GUID: " + self.getReplayGUID(replay[0], 'boxcars'))

	def exportReplayDatabase(self, header=defaultDatabaseHeader, path=defaultDatabasePath, sequential=True):
		if sequential:
			data = []
			self.databaseManager.createBackupCSV(path)
			if not self.singleBatch:
				for batch in tqdm(self.replayBatches, desc='Export progress: ', position=0):
					for replay in tqdm(batch, desc='	Batch progress: ', ncols=100, position=1):
						replay[2] = self.getReplayGUID(replay[0], 'boxcars')
						replay.append(replay.pop(0))
						data.append(replay)
						self.databaseManager.write(data, header, path, False)
			else:
				for replay in self.replayList:
					replay[2] = self.getReplayGUID(replay[0], 'boxcars')
					replay.append(replay.pop(0))
					data.append(replay)
					self.databaseManager.write(data, header, path, False)
		else:
			data = [y for x in self.replayBatches for y in x]
			self.databaseManager.write(data, header, path)

	
		#pprint(self.importedDatabase)

