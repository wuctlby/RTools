'''
Merge the tables for ML from the input files.
'''

import os
import sys
import gc
import pandas as pd
import concurrent.futures
import multiprocessing
import uproot
import ROOT
import yaml
import time
import argparse
from functools import partial

def Get_DFName(path_to_file):
    input_file = ROOT.TFile(path_to_file)
    DFName = [key.GetName() for key in input_file.GetListOfKeys()]
    print(f"DFName: {DFName}")
    if len(DFName) > 2:
        print("Warning: More than one DF in the file")
        if 'parentFiles' in DFName:
            DFName.remove('parentFiles')
        else:
            print("Error: More than one DF in the file and no 'parentFiles' found")
            exit()
    if len(DFName) == 0:
        print("Error: No DF found in the file")
        exit()
    input_file.Close()
    del input_file
    
    return DFName[0]
def merge_dataframes(*args):
    input_file, outputPath = args
    output_file = input_file.replace('.root', '_DFmerged.root')
    input_txt = os.path.join(outputPath, input_file.replace('.root', '_input.txt'))
    with open(input_txt, 'w') as f:
        f.write(input_file + '\n')
    cmd = f"o2-aod-merger --input {input_txt} --output {input_file.replace('.root', '_DFmerged.root')} --max-size 1000000000"
    os.system(cmd)
    os.remove(input_txt)
    return output_file

def merge_tables(*args):
    dfMerged_file, isMC = args
    print(f"Merging tables from {dfMerged_file} with isMC={isMC}")
    df_name = Get_DFName(dfMerged_file)
    input_file = uproot.open(dfMerged_file)
    table_merged = input_file.get(df_name)

    print('Loading tables...')
    if isMC:
        df_pt_eta_phi_mass_y = table_merged["O2hfd0base"].arrays(library="pd")
        df_mcmatchrec_origin = table_merged["O2hfd0mc"].arrays(library="pd")
        df_pars = table_merged["O2hfd0par"].arrays(library="pd")
        df_cts = table_merged["O2hfd0pare"].arrays(library="pd")
        df_selflag = table_merged["O2hfd0sel"].arrays(library="pd")

        df_merged = pd.concat([df_pt_eta_phi_mass_y, df_mcmatchrec_origin, df_pars, df_cts, df_selflag], axis=1)
        # df_merged = pd.concat([df_pt_eta_phi_mass_y, df_mcmatchrec_origin, df_pars, df_selflag], axis=1)
    else:
        df_pt_eta_phi_mass_y = table_merged["O2hfd0base"].arrays(library="pd")
        df_pars = table_merged["O2hfd0par"].arrays(library="pd")
        df_cts = table_merged["O2hfd0pare"].arrays(library="pd")
        df_selflag = table_merged["O2hfd0sel"].arrays(library="pd")

        df_merged = pd.concat([df_pt_eta_phi_mass_y, df_pars, df_cts, df_selflag], axis=1)  # DATA

    output_file = dfMerged_file.replace('_DFmerged.root', '_tableMerged.root')
    df_name = "TreeForML"  # Name for the output tree
    print(f"Writing merged table to {output_file} with df_name={df_name}")
    with uproot.recreate(output_file) as root_file:
        root_file.mktree(df_name, df_merged.dtypes.to_dict())
        root_file[df_name].extend(df_merged.to_dict(orient='list'))
    root_file.close()
    del root_file
    input_file.close()
    del input_file
    return output_file

def multi_thread(func, *args, max_workers=4):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures, results = [], []
        futures = [executor.submit(func, *arg) for arg in zip(*args)]
        for future in concurrent.futures.as_completed(futures):
            try:
                results.append(future.result()) if not isinstance(future.result(), list) else results.extend(future.result())
            except Exception as e:
                print(f"Error in thread: {e}")
    return results

def multi_process(func, *args, max_workers=4):

    with multiprocessing.Pool(processes=max_workers) as pool:
        try:
            results = pool.starmap(func, zip(*args))
            
            flat_results = []
            for result in results:
                if isinstance(result, list):
                    flat_results.extend(result)
                else:
                    flat_results.append(result)
            return flat_results
        except Exception as e:
            print(f"Error in process pool: {e}")
            raise
        finally:
            pool.close()
            pool.join()

def main(config):
    
    with open(config, 'r') as file:
        cfg = yaml.safe_load(file)
    # Load the configuration data
    inputFiles = cfg.get("inputFiles", [])
    outputPath = cfg.get("outputPath", "")
    outputName = cfg.get("outputName", time.strftime("%Y%m%d_%H%M%S") + "_merged.root")
    isMC = cfg.get("isMC", False)
    max_workers = cfg.get("max_workers", 4)
    doDFMerge = cfg.get("doDFMerge", True)
    doTableMerge = cfg.get("doTableMerge", True)
    tableMergedSuffix = cfg.get("tableMergedSuffix", "_tableMerged.root")
    doFinalMerge = cfg.get("doFinalMerge", True)
    nFile = len(inputFiles)
    
    # condition checks
    loadfile = False
    for file in inputFiles:
        if not file.endswith('.root'):
            print('Processing inputFiles as root path')
            loadfile = True
            break
    if loadfile:
        inputFiles_new = []
        for file in inputFiles:
            for root, _, files in os.walk(file):
                inputFiles_new.extend([os.path.join(root, name) for name in files if name == 'AO2D.root'])
        inputFiles = inputFiles_new
        nFile = len(inputFiles)

    if doDFMerge:
        print("Merging dataframes...")
        dfMerged_files = multi_thread(merge_dataframes, inputFiles, [outputPath]*nFile, max_workers=max_workers)
    else:
        dfMerged_files = []
        for input in cfg.get("inputFiles", []):
            for root, _, files in os.walk(input):
                dfMerged_files.extend([os.path.join(root, name) for name in files if name.endswith('_DFmerged.root')])

    if doTableMerge:
        print("Merging tables using multiprocessing...")
        tableMerged_files = []
        for i in range(0, len(dfMerged_files), max_workers):
            chunk = dfMerged_files[i:i+max_workers]
            results = multi_process(merge_tables, chunk, [isMC]*len(chunk), max_workers=max_workers)
            tableMerged_files.extend(results)
            del results
            gc.collect()
            print(f"Processed chunk {i//max_workers + 1}/{(len(dfMerged_files) + max_workers - 1) // max_workers}")
            
    else:
        dfMerged_files, tableMerged_files = [], []
        for input in cfg.get("inputFiles", []):
            for root, _, files in os.walk(input):
                tableMerged_files.extend([os.path.join(root, name) for name in files if name.endswith(tableMergedSuffix)])
                dfMerged_files.extend([os.path.join(root, name) for name in files if name.endswith('_DFmerged.root')])

    if doFinalMerge:
        print(f"Merged different files to: {outputPath}")
        os.makedirs(f"{outputPath}", exist_ok=True)
        outputName = outputName.replace(".root", "_merged.root")
        command = f"hadd -f -k -j 16 -n 2 {os.path.join(outputPath, outputName)} " + " ".join(tableMerged_files)
        os.system(command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("config", metavar="text",
                        default="./config_MergepT.yml", help="input YAML config file")
    args = parser.parse_args()

    main(
        config=args.config
    )