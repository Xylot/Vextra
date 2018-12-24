from pprint import pprint
from Parser import Decompiler, Parser
from FileManager import FileManager
from DatabaseManager import DatabaseManager, CSVManager

class FileManagerTest:
	def __init__(self):
		pass

	def test(self):
		#manager = FileManager()

		# startTime=time.time()
		# manager.writeOneByOne(path='Replay Database BC', useBC=True)
		# print('Boxcars run time: ' + str(time.time() - startTime))
		# startTime=time.time()
		# manager.writeOneByOne(path='Replay Database RT', useBC=False)
		# print('Rattletrap run time: ' + str(time.time() - startTime))

		#pprint(manager.getReplayGUID(['C:/Users/Joseph/Documents/GitHub/CalculatedGG-Uploader/Refactor/0F84A75D45E7EB7F8D174E89F9AF530F.replay']))
		# B061283E11E8FABB3863BE9B893AE1C5

		#pprint(manager.replayBatches)

		#manager.testDecompileTime()

		# Boxcars run time: 164.7187614440918 seconds - 2mins 44secs
		# Rattletrap run time: 985.8462634086609 seconds - 16mins 26secs

		# Boxcars decompile time: 124.69161868095398 seconds - 2mins 4 seconds
		# Rattletrap decompile time: 510.35151839256287 seconds - 8mins 30 seconds
		pass

class UploaderTest:
	def __init__(self):
		pass

class ReplayDatabaseManagerTest:
	def __init__(self):
		pass

	def test(self):
		# manager = ReplayDatabaseManager()
		# manager.importReplayDatabase()
		# value = manager.getGUIDFromDatabase('87B11D4743F1EAE859CAC9B48DAA8E89.replay')
		# pprint(value)
		#manager.exportReplayDatabase()
		#manager.importReplayDatabase()
		pass

	def testDecompileTime(self):
		startTime = time.time()
		for replay in tqdm(self.replayList):
			replayAnalyzer = ReplayManager(replay[0], onlyGUID=True)
		print('Boxcars run time: ' + str(time.time() - startTime))


		startTime = time.time()
		for replay in tqdm(self.replayList):
			replayAnalyzer = ReplayManager(replay[0], onlyGUID=False)
		print('Rattletrap run time: ' + str(time.time() - startTime))

class DatabaseManagerTest:
	def __init__(self):
		self.manager = DatabaseManager()
		self.cmanager = CSVManager()

		#manager.exportReplayDatabase()

	def createDatabase(self):
		pass

	def importDatabase(self, databasePath):
		return self.manager.read(databasePath)

	def exportDatabase(self, data, header, filePath, createBackup):
		self.cmanager.write(data, header, filePath, createBackup)

	def dropTest(self, colName, database):
		return self.manager.delCol(colName, database)

	def swapTest(self, cols, database):
		return self.manager.swapCols(cols, database)

	def delDuplicatesTest(self, database):
		return self.manager.delDupes(database)

	def databaseTester(self):
		testReplay = '87B11D4743F1EAE859CAC9B48DAA8E89.replay'

		# testDB = pd.read_csv(defaultDatabasePath)
		# print(testDB)

		dbm = DatabaseManager()
		dbm.read()
		#print(dbm.database)

		row = dbm.getRow(testReplay)
		print(row)
		value = row.iloc[0]['GUID']
		print(value)

		# csvManager = CSVManager()
		# reader = csvManager.Reader(testPath)
		# db = reader.database
		# print(db)
		# db1 = reader.getRow(testReplay)
		# print(db1.iloc[0]['Name'])
		# print(reader.valueExists([testReplay]))
		# #print(db1.index)

class ParserTest:

	def __init__(self):
		self.replayPath = "C:/Users/Joseph/Documents/GitHub/CalculatedGG-Uploader/Refactor/TestFiles/Replays/Set of 5/0F84A75D45E7EB7F8D174E89F9AF530F.replay"
		self.logDecompileTime = False
		self.testDecompile()
		self.getGUID()
		self.printAttributes()

	def testDecompile(self):
		self.jsonObject = Decompiler(self.replayPath).decompile(logTime=self.logDecompileTime)

	def getGUID(self):
		self.guid = Parser(self.jsonObject, 'boxcars').getGUID()

	def printAttributes(self):
		pprint('GUID: ' + self.guid)

# #parserTest = ParserTest()
# databaseManager = DatabaseManagerTest()
# db = databaseManager.importDatabase('C:/Users/Joseph/Documents/GitHub/CalculatedGG-Uploader/Refactor/Complete (With Duplicates).csv')
# #db_drop = databaseManager.dropTest('index', db)
# #db_newCols = databaseManager.swapTest(['Name', 'GUID', 'Path'], db_drop)
# db_delDupes = databaseManager.delDuplicatesTest(db)
# # print(db)
# # print(db_delDupes)
# databaseManager.exportDatabase(data=db_delDupes, header=list(db_delDupes), filePath='Complete.csv', createBackup=False)
# # tbt = databaseManager.importDatabase('C:/Users/Joseph/Documents/GitHub/CalculatedGG-Uploader/Refactor/Tobetrimmed.csv')
# # tbt_drop = databaseManager.dropTest('JSON', tbt)
# # databaseManager.exportDatabase(data=tbt_drop, header=list(tbt), filePath='tbt.csv', createBackup=False)

databaseManager = DatabaseManagerTest()
databaseManager.databaseTester()