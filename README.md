# Vextra

Vextra is a CLI Rocket League replay uploader to Calculated.gg. Vextra supports basic replay uploads from the default or specified replay folder, GUID utilization to prevent uploading duplicate replays to the server, and various other tools to faciliate replay uploading.

## Requirements

- Python 3.6+
- Windows or Mac

## Interface

| Argument | Value |                        Description                        |                               Default                              | Optional? |
|:--------:|:-----:|:---------------------------------------------------------:|:------------------------------------------------------------------:|:---------:|
|    -p    |  PATH |    The folder path of the set of replays to be uploaded   | C:/Users/%USERNAME%/Documents/My Games/Rocket League/TAGame/Demos/ |    YES    |
|    -d    |  PATH |             The file path of the guid database            |                            ReplayDB.csv                            |    YES    |
|    -c    |  NONE | Creates a guid database with the replay files in the path |                                False                               |    YES    |

## Replay Database

The database is a csv file with 3 values: replay name, replay GUID, and replay path. The GUID is the unique identifier of the replay and is used by the uploader to determine if the replay already exists in the Calculated.gg database. The replays are parsed using two different methods: [Rattletrap](https://github.com/tfausak/rattletrap)/[Carball](https://github.com/SaltieRL/carball), and [Boxcars](https://github.com/nickbabcock/boxcars). Rattletrap and carball allow for a complete analysis of each replay and boxcars is utilized for its speed in parsing the GUID of the replay file.

Note that replays pre season 6 will not parse correctly and therefore will not have a readable GUID. So, those replays will be automatically uploaded to the server.

## Uploading

This uploader will by default upload the entire replay folder located in `C:/Users/%USERNAME%/Documents/My Games/Rocket League/TAGame/Demos/`

To run the script:

    python main.py

If you do not want to upload from the default path, you can pass the argument -p followed by the folder path to upload from there instead:

    python main.py -p "C:/Users/%USERNAME%/Desktop/FolderToUpload"

To create the guid database, pass the -c argument, and optionally -p, to create the database with the name ReplayDB.csv:

    python main.py -c

    python main.py -p "C:/Users/%USERNAME%/Desktop/FolderToUpload" -c

To use a pre-created database and save upload bandwidth:

    python main.py -d "C:/Users/%USERNAME%/Desktop/ReplayDB.csv"

    python main.py -p "C:/Users/%USERNAME%/Desktop/FolderToUpload" -d "C:/Users/%USERNAME%/Desktop/ReplayDB.csv"

## Documentation

### Component Descriptions

|        Component        |                                   Description                                   |
|:-----------------------:|:-------------------------------------------------------------------------------:|
|           Main          |                              Initiates the uploader                             |
|     Database Manager    |     Reads, writes and edits the replay databases using the pandas framework     |
|       File Manager      |            Gets the attributes of the replay folder path and database           |
|          Parser         | Converts a replay into a json object and extracts bits of data such as the GUID |
| Replay Database Manager |      Iterates through the replay database and gets the GUID for each replay     |
|      Status Updater     |                  Updates the user on the current program state                  |
|         Uploader        |                       Uploads the replays to Calculated.gg                      |
|       Unit Tester       |                Tests the components and functions of the program                |