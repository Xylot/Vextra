from FileManager import FileManager
from Uploader import Uploader
from pprint import pprint

replayURL = 'https://calculated.gg/api/replay/'

def getUploadedFiles():
	fileManager = FileManager(args=[None, None, None])
	demoPathAttributes = fileManager.getAttributes()
	uploader = Uploader(demoPathAttributes)

def 


getUploadedFiles()
