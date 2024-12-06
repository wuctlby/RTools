import os
import re
import ROOT


def load_file(inputPath, keyWord):
    '''
    Load the file in the inputPath with the keyWord.

    Input:
        -inputPath:
            path to the file and the file name
        -keyWord:
            key word for the file

    Output:
        -file list
    '''
    # get list of keys in inputdir
    listofFiles = os.listdir(inputPath)
    listtoReturn = []
    # loop over all keys
    for key in listofFiles:
        # if key is the inputName
        if keyWord in key:
            listtoReturn.append(inputPath + '/' + key)

    listofFiles.sort()
    return listtoReturn


def load_histos(inputFiles, histoName):
    '''
    Load the histogram in the inputFiles with the histoName.

    Input:
        -inputFiles:
            list of input files
        -histoName:
            name of the histogram

    Output:
        -histo list
    '''
    #TODO: histo is list infile is list, histo is not list infile is list, histo is list infile is not list
    histoList = []
    # loop over all inputFiles
    for inputFile in inputFiles:
        # open the file
        file = ROOT.TFile(inputFile)
        # get the histogram
        histo = file.Get(histoName)
        histo.SetDirectory(0)
        # append the histogram to the list
        histoList.append(histo)
    return histoList


def load_runNumber(inputFiles):
    '''
    Load the run number in the inputFiles.

    Input:
        -inputFiles:
            list of input files

    Output:
        -run number list
    '''
    runNumberList = []
    # loop over all inputFiles
    for inputFile in inputFiles:
        match = re.search(r'\d{6}', inputFile)
        if match:
            runNumber = match.group(0)
            runNumberList.append(runNumber)
    runNumberList.sort()
    return runNumberList
