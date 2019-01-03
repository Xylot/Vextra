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

	# Takes in the full path of a replay file
	def __init__(self, replayPath):
		self.replayPath = replayPath
		self.getAttributes()

	# Sets the parameters needed by the decompiler
	def getAttributes(self):
		self.jsonPath = self.getJsonPath()
		self.replayName = self.getReplayName()

	# Sets the json path for use by the decompiler
	# The json path is by default stored in the same folder as the replay file
	def getJsonPath(self):
		return self.replayPath.replace('.replay', '.json')

	# Gets the file name from the full replay path
	# Currently unused
	def getReplayName(self):
		head, tail = ntpath.split(self.replayPath)
		return tail or ntpath.basename(head)

	# Decompiles the replay file to a json object
	# There are two options for a decompiler:
	# 	Rattletrap:
	#		Parses the entire replay including the network stream
	#		Mature parser and more likely to parse without error
	#		Signifcantly slower than boxcars
	#		Currently used to parse replays that fail with boxcars
	#	Boxcars:
	#		Has the option to parse the header only as well as the network stream
	#		Very fast parsing
	# Each json output must be handled differently as they are not outputted in the same format
	# Also provides the option of outputting the time taken to decompile
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

# Parse the decompiled json object and query for various properties of the replay file
class ParseFull:
	
	# Takes in decompiled json object and the parser used to decompile
	# If the replay was decompiled with rattletrap, carball is used to analyze the replay
	#	In order to analyze the replay with carball, the json object must first be initialized
	# If the replay was decompiled with boxcars, the json is parsed from scratch
	def __init__(self, jsonObject, parser):
		self.jsonObject = jsonObject
		self.parser = parser
		if parser == 'rattletrap':
			self.game = Game().initialize(loaded_json=self.jsonObject)

	# Gets the unique identifier of the replay
	# The unique identifier is used by the uploader to determine if the replay already exists on the server
	# The unique identifier is also used as a way to identify a replay after name changes and file transfers
	def getGUID(self):
		if self.parser == 'boxcars':
			self.kvGen = self.findkeys(self.jsonObject, "String")
			self.values = [x for x in self.kvGen]
			for item in self.values:
				if len(item) == 32:
					return item
		else:
			return self.game.game_info.match_guid

	# Search the json object for a specific key and return a list of the result values
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

# Parse the json header object and return important header information
class ParseHeader:

	# Takes in the decompiled json object from boxcars
	# Only extracts the useful information out of the header 
	def __init__(self, jsonObject):
		self.jsonObject = jsonObject['properties']
		self.mapDict = self.getMapDict()
		self.setHeaderData()
		self.getHeaderData()

	# Parses for all of the useful key values in the json object
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
		self.goalsBlue = self.getValue('Team0Score')	
		self.goalsOrange = self.getValue('Team1Score')
		self.teamSize = self.getValue('TeamSize')
		self.players = self.getValue('PlayerStats')
		self.replayName = self.getValue('ReplayName')

	# Creates and returns a list of the properties of the header
	# This list is used to create and modify the replay database used by the uploader as well as the desktop replay manager
	def getHeaderData(self):
		self.data = {
			'Build_ID': self.buildID,
			'Build_Version': self.buildVersion,
			'Date': self.date,
			'Game_Version': self.gameVersion,
			'Replay_Version': self.replayVersion,
			'ID': self.ID,
			'Replay_Name': self.replayName,
			'Map': self.getMapName(self.map),
			'Match_Type': self.matchType,
			'Team_Size': self.getTeamType(self.teamSize),
			'Goals_Orange': self.getGoalCount(self.goalsOrange),
			'Goals_Blue': self.getGoalCount(self.goalsBlue),
			'User': self.user,
			'Players': self.players
		}
		return self.data

	# Loads the map dictionary stored in the resouces folder into memory
	# Rocket League refers to maps by their internal map name in the replay files
	# The map dictionary is used to convert the internal map name to the recognizable map name used in game
	def getMapDict(self):
		with open('Resources/Databases/MapDatabase.json') as f:
			_json = json.load(f)
		return _json

	# Retrieves the map name from the map dictionary
	def getMapName(self, mapValue):
		return self.mapDict.get(mapValue)

	# Converts the teamsize header property to the playlist names used in game
	# Rocket league outputs the amount of players on each team instead of a playlist id to the header
	# The conversion is direct and simple, the amount of players is the playlist
	# Currently unsure on how unranked and alternative playlists (rumble, dropshot, hoops, hockey) are handled
	def getTeamType(self, teamSize):
		if teamSize == 1:
			return '1v1'
		elif teamSize == 2:
			return '2v2'
		elif teamSize == 3:
			return '3v3'
		elif teamSize == 4:
			return '4v4'
		else:
			return 'Error'

	# Converts the goal count in the header property to a useable value
	# If no goals are scored, that team's goal property will not be found in the header
	# As a result the value returned is none when no goals are scored
	def getGoalCount(self, goals):
		if goals == None:
			return 0;
		else:
			return goals

	# Searches the json object for a key and returns the first value found
	# If no values are found, none is returned
	# Since the none value is handled by each key differently, each property has their own function instead of doing it here
	def getValue(self, value):
		kvGen = self.findkeys(self.jsonObject, value)
		values = [x for x in kvGen]
		try:
			return values[0]
		except:
			return None

	# Search the json object for a specific key and return a list of the result values
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

class ParseReplayHeaderJson:
	pass
