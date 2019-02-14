import os
from shutil import copyfile
import mutagen

def readDir(musicFolderPath):
    audioFiles = []
    for root, subdirs, files in os.walk(musicFolderPath):
        for filename in files:
            if filename.endswith('.mp3'):
                fullPath = '%s/%s' % (root, filename)
                audioFiles.append({
                    'path' : fullPath,
                    'audio': mutagen.File(fullPath)
                })

    return audioFiles


def cleanMusic(audioFiles):
    cleanedAudioFiles = {}
    noAlbumEntries = []

    # Remove duplicates and entries that doesn't have a title or artist
    for audioFile in audioFiles:
        audio = audioFile['audio']
        if 'TPE1' in audio.tags:                        # Artist tag
            if 'TIT2' in audio.tags:                    # Title tag
                if 'TALB' in audio.tags :               # Album tag
                    key = ( audio.tags['TPE1'].text[0], 
                            audio.tags['TIT2'].text[0])

                    if key not in cleanedAudioFiles:
                        cleanedAudioFiles[key] = audioFile
                else:
                    noAlbumEntries.append(audioFile)

    # Keep the entry that doesn't have an album but is not present in the list
    for noAlbumAudioFile in noAlbumEntries:
        key = (audio.tags['TPE1'].text[0], 
               audio.tags['TIT2'].text[0])
        if key not in cleanedAudioFiles:
            cleanedAudioFiles[key] = noAlbumAudioFile
    
    return cleanedAudioFiles


def cleanString(string):
    # Sanitize for filename
    toReturn = string.replace('ft. ', 'ft ').replace(' ', '_').replace('/','_')
    toReturn = toReturn if toReturn[-1] != '_' else toReturn[:-1]
    toReturn = toReturn if toReturn[0]  != '_' else toReturn[1:]
    return toReturn


def writeFiles(audioFiles, outputDir):
    if not os.path.isdir(outputDir):
        os.mkdir(outputDir)

    for (artist, title), audioFile in audioFiles.items():
        cleanedArtistName = cleanString(artist)
        artistFolder = os.path.join(outputDir, cleanedArtistName)

        if not os.path.isdir(artistFolder):
            os.mkdir(artistFolder)
        
        filename = cleanedArtistName

        # Check if file has an album
        if 'TALB' in audioFile['audio'].tags:
            filename += '-' + cleanString(audioFile['audio'].tags['TALB'].text[0])

        filename += '-' + cleanString(title) + '.mp3'
        filepath = os.path.join(artistFolder, filename)

        copyfile(audioFile['path'], filepath)
        print("Copied : %s" % filename)


if __name__ == "__main__":
    inputDir = '/home/j3romee/Music/Unsorted'
    outputDir = '/home/j3romee/Music/Sorted'

    print(">>> Reading MP3 files in '%s'" % inputDir)
    audioFiles = readDir(inputDir)

    print(">>> Removing duplicates")
    cleanedAudioFiles = cleanMusic(audioFiles)
    
    print(">>> Writing to disk in '%s'" % outputDir)
    writeFiles(cleanedAudioFiles, outputDir)
    
    print('\n')
    print(">>> All done -- Duplicated and Unlabeled audio file removed")
    print(">>> Cleaned files contained in '%s'" % inputDir)
    print(">>> Have been written at '%s'" % outputDir)
    
