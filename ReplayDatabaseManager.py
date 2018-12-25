import json
from Parser import Decompiler, ParseFull, ParseHeader
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
			guid = ParseFull(jsonObject, parser).getGUID()
			if any(guid): return guid 
			else: return 'None'
		except:
			return 'Error'

	def getBatchGUIDs(self, batch):
		for replay in batch:
			replay[2] = self.getReplayGUID(replay[0], 'boxcars')
		return batch

	def getReplayHeader(self, replay, parser):
		jsonObject = Decompiler(replay).decompile(parser=parser, logTime=False)
		header = ParseHeader(jsonObject).getHeaderData()
		if any(header): return header 
		else: return 'None'
		pass

	def getBatchHeaders(self):
		for batch in self.replayBatches:
			for replay in batch:
				header = self.getReplayHeader(replay[0], 'boxcars')
				headerjson = self.dictToJson(header)
				self.outputJSON(headerjson)
		pass

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

	def dictToJson(self, dictData):
		data = json.dumps(dictData)
		loadedData = json.loads(data)
		return loadedData

	def outputJSON(self, jsonObject):
		with open('data.json', 'a') as outfile:
		    json.dump(jsonObject, outfile, indent=4, separators=(',', ': '), sort_keys=True)

    

