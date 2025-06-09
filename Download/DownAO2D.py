import os
import sys
import argparse
import concurrent.futures
import yaml
sys.path.append('../')
from utils.cook_path import get_hp_outpath

def download_files(nr, localpath, filePath):
    print(f"Downloading {filePath} to {localpath}")
    os.system(f"alien.py cp -f -T {nr} {filePath} file:{localpath}")

def download_file_wrapper(args):
    nr, localpath, filePath = args
    download_files(nr, localpath, filePath)

def main(config, check=False):
    # load configuration
    with open(config, 'r') as f:
        config = yaml.safe_load(f)
    
    # basic parameters
    nr = config.get('nr', 64)
    train_num = config.get('train_num', '414423')
    localpath = config.get('localpath', '/media/wuct/wulby/ALICE/AnRes/D0_flow/2024/Reso')
    fileName = config.get('fileName', 'AnalysisResults')
    max_workers = config.get('max_workers', 32)
    
    # paths and stages
    copypaths = config.get('copypaths', [])
    copypaths_faild = config.get('copypaths_faild', [])
    Stage_faild = config.get('Stage_faild', ['Stage_1'])

    # handle paths
    for faild_path in copypaths_faild:
        if faild_path in copypaths:
            copypaths.remove(faild_path)

    paths_sucs = get_hp_outpath(copypaths, '')
    pre_paths_faild = get_hp_outpath(copypaths_faild, '')
    
    if len(Stage_faild) == 1 and len(Stage_faild) < len(pre_paths_faild):
        Stage_faild = [Stage_faild[0]] * len(pre_paths_faild)

    paths_faild = [path + '/' + stage for path in pre_paths_faild for stage in Stage_faild]

    # Download files
    if check:
        print("Check mode is enabled. No files will be downloaded.")
        for ipath, path in enumerate(paths_sucs):
            file_to_check = f"{localpath}/{train_num}/{ipath}/{fileName}.root"
            if not os.path.isfile(file_to_check):
                print(f"File does not exist: {file_to_check} ==> {path}")
    else:
        print("Starting file download...")
        if paths_sucs != ['']:
            down_task = [(nr, 
                            f"{localpath}/{train_num}/{ipath}/{fileName}.root", 
                            f"{path}/{fileName}.root",
                            ) for ipath, path in enumerate(paths_sucs)]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                executor.map(download_file_wrapper, down_task)

        if copypaths_faild != ['']:
            down_task_faild = [(nr, 
                                f"{localpath}/{train_num}/{ipath + len(paths_sucs)}",
                                f"{path}/*{fileName}.root",
                                ) for ipath, path in enumerate(paths_faild)]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                executor.map(download_file_wrapper, down_task_faild)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download files from Alien")
    parser.add_argument("--config", metavar="text",
                    default="./config/DownAO2D.yaml", help="configuration file")
    parser.add_argument("--check", '-c', action='store_true',
                        help="check the Download files")
    args = parser.parse_args()

    if args.check:
        print("Check mode is enabled. No files will be downloaded.")
        main(args.config, check=True)
    else:
        main(args.config)