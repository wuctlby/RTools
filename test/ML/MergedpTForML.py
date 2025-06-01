'''
Merge the tables for ML from the input files.
'''

# import os
# import argparse
# import yaml
# import concurrent.futures
# from alive_progress import alive_bar
# import pandas as pd
# import ROOT
# import uproot

# def get_root_keys(path_to_file):
#     """Get list of keys from a ROOT file."""
#     input_file = ROOT.TFile(path_to_file)
#     keys = [key.GetName() for key in input_file.GetListOfKeys()]
#     input_file.Close()
#     return keys

# def merge_dataframes(input_files, output_pattern):
#     """
#     Merge input ROOT files into single output file using o2-aod-merger.
    
#     Args:
#         input_files: List of input file paths
#         output_pattern: Pattern for output filename (from config)
#     """
#     output_file = os.path.join(os.path.dirname(input_files[0]), output_pattern)
#     if not input_files:
#         raise ValueError("No input files provided")
        
#     input_dir = os.path.dirname(input_files[0])
#     input_list = os.path.join(input_dir, 'input.txt')
    
#     with open(input_list, 'w') as f:
#         for file in input_files:
#             f.write(file + '\n')
    
#     cmd = f"o2-aod-merger --input {input_list} --output {output_file} --max-size 1000000000"
#     os.system(cmd)
#     return output_file

# def merge_tables(input_file, isMC, output_pattern):
#     """
#     Merge tables from input ROOT file into ML-ready format.
    
#     Args:
#         input_file: Input ROOT file path
#         isMC: Whether processing MC data  
#         output_pattern: Output filename pattern (from config)
#     Returns:
#         Path to merged output file
#     """
#     output_suffix = output_pattern
#     df_name = get_root_keys(input_file)[0]
#     input_data = uproot.open(input_file)
#     table = input_data[df_name]
    
#     # Extract and merge relevant tables
#     base_df = table["O2hfd0base"].arrays(library="pd")
#     pars_df = table["O2hfd0par"].arrays(library="pd")
#     selflag_df = table["O2hfd0sel"].arrays(library="pd")
    
#     if isMC:
#         mc_df = table["O2hfd0mc"].arrays(library="pd")
#         merged_df = pd.concat([base_df, mc_df, pars_df, selflag_df], axis=1)
#     else:
#         cts_df = table["O2hfd0pare"].arrays(library="pd")
#         merged_df = pd.concat([base_df, pars_df, cts_df, selflag_df], axis=1)
    
#     # Write merged data to new ROOT file
#     output_file = input_file.replace(".root", output_suffix)
#     with uproot.recreate(output_file) as out_file:
#         out_file.mktree("TreeForML", merged_df.dtypes.to_dict())
#         out_file["TreeForML"].extend(merged_df.to_dict(orient='list'))
    
#     return output_file

# def process_files_parallel(file_list, isMC, max_workers=4):
#     """Process list of files in parallel using ThreadPoolExecutor."""
#     with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
#         with alive_bar(len(file_list), title='Merging Tables') as bar:
#             futures = []
#             for file in file_list:
#                 futures.append(executor.submit(merge_tables, file, isMC))
            
#             results = []
#             for future in concurrent.futures.as_completed(futures):
#                 results.append(future.result())
#                 bar()
#     return results

# def main(config_path):
#     """Main function to execute merging workflow."""
#     with open(config_path) as f:
#         config = yaml.safe_load(f)
    
#     input_files = config["inputFiles"]
#     isMC = config["isMC"]
#     max_workers = config.get("max_works", 4)
#     df_output_pattern = config.get("dfOutputPattern", "merged.root")
#     table_output_pattern = config.get("tableOutputPattern", "_tableMerged.root")
#     final_output_pattern = config.get("finalOutputPattern", f"final_{df_output_pattern}")
    
#     if config["doMergeDF"]:
#         print("Merging dataframes...")
#         merge_dataframes(input_files, df_output_pattern)
    
#     if config["doMergeTable"]:
#         print("Merging tables...")
#         if config["doMergeDF"]:
#             # Use the merged DF file
#             table_input = merge_dataframes(input_files, df_output_pattern)
#         else:
#             # Use original input files
#             table_input = input_files[0]
        
#         merged_tables = process_files_parallel([table_input], isMC, max_workers)
        
#         if config["doFinalMerge"]:
#             print("Final merging...")
#             final_output = os.path.join(os.path.dirname(input_files[0]), final_output_pattern)
#             cmd = f"hadd -f {final_output} {' '.join(merged_tables)}"
#             os.system(cmd)

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Merge ROOT files for ML analysis")
#     parser.add_argument("config", help="Path to YAML config file")
#     args = parser.parse_args()
#     main(args.config)


import os
import sys
import pandas as pd
import uproot
import ROOT
import yaml
import time
import argparse

def Get_DFName(path_to_file):
    input_file = ROOT.TFile(path_to_file)
    DFName = [key.GetName() for key in input_file.GetListOfKeys()]
    print(f"DFName: {DFName}")
    if len(DFName) > 2:
        print("Warning: More than one DF in the file")
        exit()
    input_file.Close()
    
    return DFName[0]

def merge_dataframes(input_files, outputPath, outputName):
    input_txt = os.path.join(outputPath, 'input.txt')
    with open(input_txt, 'w') as f:
        for file in input_files:
            f.write(file + '\n')
    output_file = os.path.join(outputPath, outputName + '_DFmerged.root')
    cmd = f"o2-aod-merger --input {input_txt} --output {output_file} --max-size 1000000000"
    os.system(cmd)
    return output_file

def merge_tables(dfMerged_file, isMC, outputPath, outputName):
    df_name = Get_DFName(dfMerged_file)
    input_file = uproot.open(dfMerged_file)
    table_merged = input_file.get(df_name)

    if isMC:
        df_pt_eta_phi_mass_y = table_merged["O2hfd0base"].arrays(library="pd")
        df_mcmatchrec_origin = table_merged["O2hfd0mc"].arrays(library="pd")
        df_pars = table_merged["O2hfd0par"].arrays(library="pd")
        # df_cts = table_merged["O2hfd0pare"].arrays(library="pd")
        df_selflag = table_merged["O2hfd0sel"].arrays(library="pd")

        df_merged = pd.concat([df_pt_eta_phi_mass_y, df_mcmatchrec_origin, df_pars, df_selflag], axis=1)  # MC
    else:
        df_pt_eta_phi_mass_y = table_merged["O2hfd0base"].arrays(library="pd")
        df_pars = table_merged["O2hfd0par"].arrays(library="pd")
        df_cts = table_merged["O2hfd0pare"].arrays(library="pd")
        df_selflag = table_merged["O2hfd0sel"].arrays(library="pd")

        df_merged = pd.concat([df_pt_eta_phi_mass_y, df_pars, df_cts, df_selflag], axis=1)  # DATA

    output_file = os.path.join(outputPath, outputName + '_TableMerged.root')
    df_name = "TreeForML"  # Name for the output tree
    with uproot.recreate(output_file) as root_file:
        root_file.mktree(df_name, df_merged.dtypes.to_dict())
        root_file[df_name].extend(df_merged.to_dict(orient='list'))
    root_file.close()
    input_file.close()

    return output_file
    

def main(config):
    
    with open(config, 'r') as file:
        cfg = yaml.safe_load(file)
    # Load the configuration data
    inputFiles = cfg.get("inputFiles", [])
    outputPath = cfg.get("outputPath", "")
    outputName = cfg.get("outputName", time.strftime("%Y%m%d_%H%M%S") + "_merged.root")
    isMC = cfg.get("isMC", False)
    
    print("Merging dataframes...")
    dfMerged_file = merge_dataframes(inputFiles, outputPath, outputName)
    
    print("Merging tables...")
    tableMerged_file = merge_tables(dfMerged_file, isMC, outputPath, outputName)
    
    print(f"Dataframes merged to: {dfMerged_file}")
    print(f"Tables merged to: {tableMerged_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("config", metavar="text",
                        default="config_MergepT.yml", help="input YAML config file")
    args = parser.parse_args()

    main(
        config=args.config
    )