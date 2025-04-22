import os
import re
import ROOT
from typing import List


def load_file(inputPath, keyWord, recursive=True):
    '''
    Load the file in the inputPath with the keyWord.

    Input:
        -inputPath:
            path to the file and the file name
        -keyWord:
            key word for the file
        -whether to search recursively

    Output:
        -file list
    '''
    matched_files = []
    
    if not os.path.isdir(inputPath):
        raise ValueError(f"输入路径不存在或不是目录: {inputPath}")

    for root, dirs, files in os.walk(inputPath):
        for file in files:
            if keyWord in file:
                full_path = os.path.join(root, file)
                matched_files.append(full_path)

        if not recursive:
            break

    # 按文件名排序
    matched_files.sort()
    return matched_files


def load_histos(inputFiles, histoName, keyWord = False, onlyPath = False):
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
    if not isinstance(inputFiles, List):
        inputFiles = [inputFiles]
    if not keyWord:
        # loop over all inputFiles
        for inputFile in inputFiles:
            # open the file
            file = ROOT.TFile(inputFile)
            # get the list of histograms
            objNames = load_non_dir_objects(file)
            for objName in objNames:
                if objName == histoName:
                    if onlyPath:
                        histoList.append(objName)
                    else:
                        histo = file.Get(objName)
                        if isinstance(histo, ROOT.TH1):
                            histo.SetDirectory(0)
                            histoList.append(histo)
        if histoList == []:
            print(f"No histogram with the name {histoName} in the input files.")
    else:
        # loop over all inputFiles
        for inputFile in inputFiles:
            # open the file
            file = ROOT.TFile(inputFile)
            # get the list of histograms
            objNames = load_non_dir_objects(file)
            for objName in objNames:
                if histoName in objName:
                    if onlyPath:
                        histoList.append(objName)
                    else:
                        histo = file.Get(objName)
                        if isinstance(histo, ROOT.TH1):
                            histo.SetDirectory(0)
                            histoList.append(histo)
        if histoList == []:
            print(f"No histogram with the name {histoName} in the input files.")

    return histoList

def load_non_dir_objects(inputFile, path = ""):
    '''
    Return the list of non-directory objects with the path in the input file.

    Input:
        -inputFile:
            input file

    Output:
        -object list
    '''
    objectList = []
    try:
        if isinstance(inputFile, str):
            # open the file
            file = ROOT.TFile(inputFile)
            # get the list of keys
            listofKeys = file.GetListOfKeys()
        elif isinstance(inputFile, ROOT.TDirectory):
            # get the list of keys
            listofKeys = inputFile.GetListOfKeys()
        elif isinstance(inputFile, ROOT.TFile):
            # get the list of keys
            listofKeys = inputFile.GetListOfKeys()
        else:
            raise TypeError("Input file type not supported.")
    except Exception as e:
        print(f"Error: {e}")
        return objectList

    # loop over all keys
    for key in listofKeys:
        obj = key.ReadObj()
        # if the key is a directory
        if obj.IsA().InheritsFrom(ROOT.TDirectory.Class()):
            # traverse the directory
            objectList.extend(load_non_dir_objects(obj, path = path + obj.GetName() + '/'))
        else:
            objectList.append(path + obj.GetName())

    return objectList

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
