'''
Merge the tables for ML from the input files.
'''

import os
import sys
import pandas as pd
import concurrent.futures
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
        exit()
    if len(DFName) == 0:
        print("Error: No DF found in the file")
        exit()
    input_file.Close()
    
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
        df_cts = table_merged["O2hfd0pbase"].arrays(library="pd")
        df_selflag = table_merged["O2hfd0sel"].arrays(library="pd")

        df_merged = pd.concat([df_pt_eta_phi_mass_y, df_pars, df_cts, df_selflag], axis=1)  # DATA

    output_file = dfMerged_file.replace('_DFmerged.root', '_tableMerged.root')
    df_name = "TreeForML"  # Name for the output tree
    print(f"Writing merged table to {output_file} with df_name={df_name}")
    with uproot.recreate(output_file) as root_file:
        root_file.mktree(df_name, df_merged.dtypes.to_dict())
        root_file[df_name].extend(df_merged.to_dict(orient='list'))
    root_file.close()
    input_file.close()
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

def main(config):
    
    with open(config, 'r') as file:
        cfg = yaml.safe_load(file)
    # Load the configuration data
    inputFiles = cfg.get("inputFiles", [])
    outputPath = cfg.get("outputPath", "")
    outputName = cfg.get("outputName", time.strftime("%Y%m%d_%H%M%S") + "_merged.root")
    isMC = cfg.get("isMC", False)
    nFile = len(inputFiles)
    
    print("Merging dataframes...")
    dfMerged_files = multi_thread(merge_dataframes, inputFiles, [outputPath]*nFile)
    print("Merging tables...")
    tableMerged_files = multi_thread(merge_tables, dfMerged_files, [isMC]*nFile)
    
    print(f"Merged different files to: {outputPath}")
    with open(f'{outputPath}/input.txt', 'w') as f:
        for file in tableMerged_files:
            f.write(file + '\n')
    outputName = outputName.replace(".root", "_merged.root")
    command = f"hadd -f {os.path.join(outputPath, outputName)} " + " ".join(tableMerged_files)
    os.system(command)

    print(f"Final merged file: {os.path.join(outputPath, outputName)}")
    if os.path.exists(os.path.join(outputPath, outputName)):
        for file in tableMerged_files + dfMerged_files:
            if os.path.exists(os.path.join(outputPath, file)):
                os.remove(os.path.join(outputPath, file))
            if os.path.exists(os.path.join(outputPath, 'input.txt')):
                os.remove(os.path.join(outputPath, 'input.txt'))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("config", metavar="text",
                        default="./config_MergepT.yml", help="input YAML config file")
    args = parser.parse_args()

    main(
        config=args.config
    )