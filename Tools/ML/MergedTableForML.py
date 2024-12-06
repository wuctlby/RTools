import pandas as pd
import ROOT
import uproot3 as uproot
import os
import concurrent.futures

# merge DF for singe file. merge table for singe file. merge all file

# paralize file at same time
def paralize_merge(DF_merged):
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

    input_file = uproot.open(path_to_file)
    DFName = input_file.keys()
    if len(DFName) > 2:
        print("Warning: More than one DF in the file")
        exit()
    
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
            if key == inputName:
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
        tree_pt_eta_phi_mass_y = table_merged.get("O2hfd0base")
        tree_mcmatchrec_origin = table_merged.get("O2hfd0mc")
        tree_pars = table_merged.get("O2hfd0par")
        tree_cts = table_merged.get("O2hfd0pare")
        tree_selflag = table_merged.get("O2hfd0sel")

        df_pt_eta_phi_mass_y = tree_pt_eta_phi_mass_y.pandas.df()
        df_mcmatchrec_origin = tree_mcmatchrec_origin.pandas.df()
        df_pars = tree_pars.pandas.df()
        df_cts = tree_cts.pandas.df()
        df_selflag = tree_selflag.pandas.df()

        df_merged = pd.concat([df_pt_eta_phi_mass_y, df_mcmatchrec_origin, df_pars, df_cts, df_selflag], axis=1)  # MC
    else:
        tree_pt_eta_phi_mass_y = table_merged.get("O2hfd0base")
        tree_pars = table_merged.get("O2hfd0par")
        tree_cts = table_merged.get("O2hfd0pare")
        tree_selflag = table_merged.get("O2hfd0sel")

        df_pt_eta_phi_mass_y = tree_pt_eta_phi_mass_y.pandas.df()
        df_pars = tree_pars.pandas.df()
        df_cts = tree_cts.pandas.df()
        df_selflag = tree_selflag.pandas.df()

        df_merged = pd.concat([df_pt_eta_phi_mass_y, df_pars, df_cts, df_selflag], axis=1) # DATA

    outputName = path_to_file.replace(".root", "_tableMerged.root")
    if not findDF:
        DFName = "TreeForML"
    with uproot.recreate(outputName) as root_file:
        root_file[DFName] = uproot.newtree(df_merged.dtypes.to_dict())
        root_file[DFName].extend(df_merged.to_dict(orient='list'))
    root_file.close()
    input_file.close()
    
    return outputName


# inputdir= '/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/ML/DATA/297182'
# inputName = "AO2D.root"

# inputdir= '/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/ML/DATA/303753'
# inputName = "AO2D.root"

inputdir= '/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/ML/MC'
inputName = 'AO2D_medium_304463_CombPID.root'

isMC = True # True for MC, False for DATA
doMergeDF = True
doMergeTable = True
doFinalMerge = True

DF_merged_list, Table_merged_list = [], []

# merger DF for singe file
if doMergeDF:
    print('Merging DF for singe file...')
    DF_merged_list = merge_DF_singeFile(inputdir, inputName)

# merge tables for ML, if doMergedF is True
if doMergeTable and doMergeDF:
    print('Merging tables for ML...')
    with concurrent.futures.ThreadPoolExecutor(max_workers=24) as executor:
        Table_merged_list = list(executor.map(paralize_merge, DF_merged_list))

# merge tables for ML, if doMergedF is False, get the DFMerged file first
elif doMergeTable and not doMergeDF:
    print('Merging tables for ML...')
    inputNameDF = inputName.replace(".root", "_DFmerged.root")
    # get the DFmerged file
    DF_merged_list = merge_DF_singeFile(inputdir, inputNameDF, False)
    # merge tables for ML
    with concurrent.futures.ThreadPoolExecutor(max_workers=24) as executor:
        Table_merged_list = list(executor.map(paralize_merge, DF_merged_list))

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

