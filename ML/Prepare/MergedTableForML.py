import pandas as pd
import ROOT
import uproot
import argparse
import yaml
import os
import concurrent.futures
from alive_progress import alive_bar

# merge DF for singe file. merge table for singe file. merge all file

# paralize file at same time
def paralize_merge(DF_merged, isMC):
    return merge_tables_for_ml(DF_merged, isMC)

def Get_DFName(path_to_file):
    '''
    Get the DF from the input file.

    Input:
        -path_to_file:
            path to the file and the file name
    
    Output:
        -DFName:
    '''

    # input_file = uproot.open(path_to_file)
    # DFName = input_file.keys()
    input_file = ROOT.TFile(path_to_file)
    DFName = [key.GetName() for key in input_file.GetListOfKeys()]
    if len(DFName) > 2:
        print("Warning: More than one DF in the file")
        exit()
    input_file.Close()
    
    return DFName[0]

def merge_DF_singeFile(inputdirs, inputName, doMerge=True):
    '''
    Merge DF for the all inputName in the inputdirs, and return the list of merged files.

    Input:
        -inputdirs:
            list of input directories
        -inputName:
            name of the file needed to be merged.
        -doMerge:
            True for merge DF, False for not merge DF
    
    Output:
        -list of merged files
    '''
    DF_merged_list = []
    # make sure inputdirs is a list
    if not isinstance(inputdirs, list):
        inputdirs = [inputdirs]
    
    # loop over all inputdirs
    for inputdir in inputdirs:
        # get list of keys in inputdir
        listofkeys = os.listdir(inputdir)
        # loop over all keys
        for key in listofkeys:
            # if key is the inputName, write the path to input.txt
            if inputName in key:
                # get tge outfile name
                keyName = key.split(".")[0]
                if doMerge:
                    with open(f'{inputdir}/input.txt', 'w') as f:
                        f.write(inputdir + '/' + key)
                    command = f"o2-aod-merger --input {inputdir}/input.txt --output {inputdir}/{keyName}_DFmerged.root --max-size 1000000000"
                    os.system(command)
                    DF_merged_list.append(f'{inputdir}/{keyName}_DFmerged.root')
                else:
                    DF_merged_list.append(f'{inputdir}/{keyName}.root')
            # if key is a directory, call get_files recursively
            elif os.path.isdir(inputdir + '/' + key):
                if doMerge:
                    DF_merged_list.extend(merge_DF_singeFile([inputdir + '/' + key], inputName))
                else:
                    DF_merged_list.extend(merge_DF_singeFile([inputdir + '/' + key], inputName, False))
    return DF_merged_list

def merge_tables_for_ml(path_to_file, isMC, findDF=False):

    DFName = Get_DFName(path_to_file)

    input_file = uproot.open(path_to_file)
    table_merged = input_file.get(DFName)

    if isMC:
        df_pt_eta_phi_mass_y = table_merged["O2hfd0base"].arrays(library="pd")
        df_mcmatchrec_origin = table_merged["O2hfd0mc"].arrays(library="pd")
        df_pars = table_merged["O2hfd0par"].arrays(library="pd")
        df_cts = table_merged["O2hfd0pare"].arrays(library="pd")
        df_selflag = table_merged["O2hfd0sel"].arrays(library="pd")

        df_merged = pd.concat([df_pt_eta_phi_mass_y, df_mcmatchrec_origin, df_pars, df_cts, df_selflag], axis=1)  # MC
    else:
        df_pt_eta_phi_mass_y = table_merged["O2hfd0base"].arrays(library="pd")
        df_pars = table_merged["O2hfd0par"].arrays(library="pd")
        df_cts = table_merged["O2hfd0pare"].arrays(library="pd")
        df_selflag = table_merged["O2hfd0sel"].arrays(library="pd")

        df_merged = pd.concat([df_pt_eta_phi_mass_y, df_pars, df_cts, df_selflag], axis=1)  # DATA

    outputName = path_to_file.replace(".root", "_tableMerged.root")
    if not findDF:
        DFName = "TreeForML"
    with uproot.recreate(outputName) as root_file:
        root_file.mktree(DFName, df_merged.dtypes.to_dict())
        root_file[DFName].extend(df_merged.to_dict(orient='list'))
    root_file.close()
    input_file.close()
    
    return outputName

def merge(config):
    '''
    Merge the tables for ML.
    
    Input:
        -config:
            configuration file
    '''
    

    # load the configuration
    with open(config, "r") as cf:
        config = yaml.safe_load(cf)
        
    doMergeDF = config["doMergeDF"]
    doMergeTable = config["doMergeTable"]
    doFinalMerge = config["doFinalMerge"]
    inputdir = config["inputdir"]
    inputName = config["inputName"]
    isMC = config["isMC"]
    
    Max_works = config["max_works"]

    DF_merged_list, Table_merged_list = [], []

    # merger DF for singe file
    if doMergeDF:
        print('Merging DF for singe file...')
        DF_merged_list = merge_DF_singeFile(inputdir, inputName)

    # merge tables for ML, if doMergedF is True
    if doMergeTable and doMergeDF:
        print('Merging tables for ML...')
        with concurrent.futures.ThreadPoolExecutor(max_workers=Max_works) as executor:
            with alive_bar(len(DF_merged_list), title='Merging Tables') as bar:
                futures = {executor.submit(paralize_merge, df, isMC): df for df in DF_merged_list}
                Table_merged_list = []
                for future in concurrent.futures.as_completed(futures):
                    Table_merged_list.append(future.result())
                    bar()

    # merge tables for ML, if doMergedF is False, get the DFMerged file first
    elif doMergeTable and not doMergeDF:
        print('Merging tables for ML...')
        inputNameDF = inputName.replace(".root", "_DFmerged.root")
        # get the DFmerged file
        DF_merged_list = merge_DF_singeFile(inputdir, inputNameDF, False)
        # merge tables for ML
        with concurrent.futures.ThreadPoolExecutor(max_workers=Max_works) as executor:
            with alive_bar(len(DF_merged_list), title='Merging Tables') as bar:
                futures = {executor.submit(paralize_merge, df, isMC): df for df in DF_merged_list}
                Table_merged_list = []
                for future in concurrent.futures.as_completed(futures):
                    Table_merged_list.append(future.result())
                    bar()

    # final merging
    if doFinalMerge:
        print('Final merging...')
        if os.path.exists(f'{inputdir}/input.txt'):
            os.remove(f'{inputdir}/input.txt')
        if doMergeTable:
            with open(f'{inputdir}/input.txt', 'a') as f:
                for file in Table_merged_list:
                    f.write(file + '\n')
            inputName = inputName.replace(".root", "_merged.root")
            command = f"hadd -f {inputdir}/{inputName} " + " ".join(Table_merged_list)
            os.system(command)
        else:
            inputNameTable = inputName.replace(".root", "_DFmerged_tableMerged.root")
            Table_merged_list = merge_DF_singeFile(inputdir, inputNameTable, False)
            with open(f'{inputdir}/input.txt', 'a') as f:
                for iFile, file in enumerate(Table_merged_list):
                    f.write(file + '\n')
            inputName = inputName.replace(".root", "_merged.root")
            command = f"hadd -f {inputdir}/{inputName} " + " ".join(Table_merged_list)
            os.system(command)

    # if not doMergeDF and not doFinalMerge and doMergeTable:
    #     root_list = merge_DF_singeFile(inputdir, inputName, False)
    #     inputNameAll = inputName.replace(".root", "_All.root")
    #     if not os.path.exists(f'{inputdir}/{inputNameAll}'):
    #         print('Merging all files...')
    #         if os.path.exists(f'{inputdir}/input.txt'):
    #             os.remove(f'{inputdir}/input.txt')
    #         with open(f'{inputdir}/input.txt', 'a') as f:
    #             for file in root_list:
    #                 f.write(file + '\n')
    #         command = f"o2-aod-merger --input {inputdir}/input.txt --output {inputdir}/{inputNameAll} --max-size 10000000000"
    #         os.system(command)
    #     merge_tables_for_ml(f'{inputdir}/{inputNameAll}', isMC, False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("config", metavar="text",
                        default="config_PreSample.yml", help="the prepare sample configuration file")
    args = parser.parse_args()
    merge(
        config=args.config
    )