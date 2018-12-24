import csv
import shutil
import os
import numpy as np
import pandas as pd
from datetime import datetime
from pprint import pprint

defaultDatabasePath = 'ReplayDB.csv'
defaultDatabaseHeader = ['Name', 'GUID', 'Path']

class CSVManager:

	def __init__(self):
		self.filePath = defaultDatabasePath
		self.backupManager = BackupManager()

	def write(self, data, header, filePath=None, createBackup=True):
		if filePath is None: filePath = self.filePath
		if createBackup: self.backupManager.createBackup(filePath)
		data.to_csv(filePath, columns=header, index=False)

	def read(self, filePath=None):
		if filePath is None: filePath = self.filePath
		return pd.read_csv(filePath)

class DatabaseManager:

	def __init__(self):
		self.csvManager = CSVManager()
		self.backupManager = BackupManager(defaultDatabasePath)

	def read(self, filePath=defaultDatabasePath):
		self.database = self.csvManager.read(filePath)
		return self.database

	def write(self, data, header=defaultDatabaseHeader, filePath=defaultDatabasePath, createBackup=True):
		data = self.createDataFrame(data, defaultDatabaseHeader)
		self.csvManager.write(data, defaultDatabaseHeader, filePath, createBackup)

	def createDataFrame(self, data, header):
		return pd.DataFrame(data, columns=header)

	def createEmptyDataframe(self):
		database = pd.DataFrame(np.random.randint(0,100,size=(1, 3)), columns=defaultDatabaseHeader)
		database['Name'] = database.Name.astype(str)
		return database

	def getRow(self, value, database=None, colName='Name'):
		if database is None: database = self.database

		if value not in database.Name.values:
			return None

		return database[database[colName] == value]

	def getCol(self, colName, database=None):
		if database is None: database = self.database
		return database[colName]

	def delCol(self, colName, database=None):
		if database is None: database = self.database
		return database.drop(columns=[colName])

	def swapCols(self, newCols, database=None):
		if database is None: database = self.database
		return database.reindex(columns=newCols)

	def delDupes(self, database):
		if database is None: database = self.database
		return database.drop_duplicates(keep='first')

	def appendRow(self, database):
		if database is None: database = self.database

	def valueExists(self, value, database=None):
		if database is None: database = self.database
		return database.isin(value).any()

	def matchValue(self, value):
		pass

	def createBackupCSV(self, filePath=None):
		if filePath is None: filePath = defaultDatabasePath
		self.backupManager.createBackup(filePath)

class BackupManager:

	def __init__(self, filePath=None):
		if filePath is None: self.filePath = defaultDatabasePath
		else: self.filePath = filePath
		self.dbExists = self.databaseExists(filePath)

	def databaseExists(self, filePath=None):
		if filePath is None: filePath = self.filePath
		return os.path.isfile(filePath)

	def getLastModifiedTime(self, filePath=None):
		if filePath is None: filePath = self.filePath
		epoch = os.path.getmtime(filePath)
		convertedEpoch = datetime.fromtimestamp(epoch).strftime(' %Y-%m-%d %H_%M_%S')
		return convertedEpoch

	def getBackupFileName(self, filePath=None):
		if filePath is None: filePath = self.filePath
		fileNameModifier = self.getLastModifiedTime(filePath) + '.csv'
		return filePath.replace('.csv', fileNameModifier)

	def createBackup(self, filePath=None):
		if filePath is None: filePath = defaultDatabasePath
		if self.dbExists: shutil.copy2(filePath, self.getBackupFileName())

class GoogleSheetsManager:
	pass

