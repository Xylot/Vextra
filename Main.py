import argparse
import sys
from FileManager import FileManager
from Uploader import Uploader
from pprint import pprint

def main():

	args = parseArguments()
	fileManager = FileManager(args=args)
	demoPathAttributes = fileManager.getAttributes()
	uploader = Uploader(demoPathAttributes)
	uploader.upload()
	

def parseArguments():

	possibleArguments = ['-p', '-d', '-c']
	args = sys.argv[1:]

	# Demo Path
	if '-p' in args:
		nextArg = args[args.index('-p') + 1]
		if nextArg not in possibleArguments:
			demoPath = nextArg
		else:
			demoPath = None
	else:
		demoPath = None

	# Database Path
	if '-d' in args:
		nextArg = args[args.index('-d') + 1]
		if nextArg not in possibleArguments:
			databasePath = nextArg
		else:
			databasePath = None
	else:
		databasePath = None

	# Create database
	if '-c' in args:
		createDatabase = True
	else:
		createDatabase = False

	return [demoPath, databasePath, createDatabase]



if __name__ == '__main__':
	main()