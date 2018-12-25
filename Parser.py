import sys
import ntpath
import subprocess
import time
import carball
import os.path
import json
from carball.json_parser.game import Game
from subprocess import Popen, PIPE, STDOUT
from pprint import pprint

# Decompile a replay file and return a json object
class Decompiler:

	def __init__(self, replayPath):
		self.replayPath = replayPath
		self.getAttributes()

	def getAttributes(self):
		self.jsonPath = self.getJsonPath()
		self.replayName = self.getReplayName()

	def getJsonPath(self):
		return self.replayPath.replace('.replay', '.json')

	def getReplayName(self):
		head, tail = ntpath.split(self.replayPath)
		return tail or ntpath.basename(head)

	def decompile(self, parser='boxcars', logTime=False, startTime=time.time(), onlyHeader=False):
		try:
			if parser == 'boxcars':
				if onlyHeader:
					args = ['rrrocket.exe', self.replayPath]
				else:
					args = ['rrrocket.exe', '-n', self.replayPath]
				output = Popen(args, stdout=PIPE).communicate()[0].decode()
				_json = json.loads(output)
			else:
				_json = carball.decompile_replay(self.replayPath, self.jsonPath, overwrite=True)
				os.remove(self.jsonPath)

			if logTime: print('Decompile time: ' + str(time.time() - startTime))
			return _json
		except:
			print('Could not decompile replay')
			return None

# Parse the json object and return various attributes
class ParseFull:
	
	def __init__(self, jsonObject, parser):
		self.jsonObject = jsonObject
		self.parser = parser
		if parser == 'rattletrap':
			self.game = Game().initialize(loaded_json=self.jsonObject)

	def getGUID(self):
		if self.parser == 'boxcars':
			self.kvGen = self.findkeys(self.jsonObject, "String")
			self.values = [x for x in self.kvGen]
			for item in self.values:
				if len(item) == 32:
					return item
		else:
			return self.game.game_info.match_guid

	def findkeys(self, node, kv):
		if isinstance(node, list):
		    for i in node:
		        for x in self.findkeys(i, kv):
		            yield x
		elif isinstance(node, dict):
		    if kv in node:
		        yield node[kv]
		    for j in node.values():
		        for x in self.findkeys(j, kv):
		            yield x

class ParseHeader:

	def __init__(self, jsonObject):
		self.jsonObject = jsonObject['properties']
		self.setHeaderData()
		self.getHeaderData()

	def setHeaderData(self):
		self.buildID = self.getValue('BuildID')
		self.buildVersion = self.getValue('BuildVersion')
		self.date = self.getValue('Date')
		self.gameVersion = self.getValue('GameVersion')
		self.replayVersion = self.getValue('ReplayVersion')
		self.ID = self.getValue('Id')
		self.map = self.getValue('MapName')
		self.matchType = self.getValue('MatchType')
		self.user = self.getValue('PlayerName')
		self.goalsOrange = self.getValue('Team0Score')
		self.goalsBlue = self.getValue('Team1Score')
		self.teamSize = self.getValue('TeamSize')
		self.players = self.getValue('PlayerStats')

	def getHeaderData(self):
		self.data = {
			'Build_ID': self.buildID,
			'Build_Version': self.buildVersion,
			'Date': self.date,
			'Game_Version': self.gameVersion,
			'Replay_Version': self.replayVersion,
			'ID': self.ID,
			'Map': self.map,
			'Match_Type': self.matchType,
			'Team_Size': self.teamSize,
			'Goals_Orange': self.goalsOrange,
			'Goals_Blue': self.goalsBlue,
			'User': self.user,
			'Players': self.players
		}
		return self.data

	def getValue(self, value):
		kvGen = self.findkeys(self.jsonObject, value)
		values = [x for x in kvGen]
		try:
			return values[0]
		except:
			return None

	def findkeys(self, node, kv):
		if isinstance(node, list):
		    for i in node:
		        for x in self.findkeys(i, kv):
		            yield x
		elif isinstance(node, dict):
		    if kv in node:
		        yield node[kv]
		    for j in node.values():
		        for x in self.findkeys(j, kv):
		            yield x
