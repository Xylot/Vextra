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

	def decompile(self, parser='boxcars', logTime=False, startTime=time.time()):
		try:
			if parser == 'boxcars':
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
class Parser:
	
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