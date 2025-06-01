import os
import sys
import concurrent.futures
sys.path.append('../')
from utils.cook_path import get_hp_outpath


def download_files(nr, localpath, filePah):
    os.system(f"alien.py cp -f -T {nr} {filePah} file:{localpath} | echo WUlby129941")
    
def download_file_wrapper(args):
    nr, localpath, filePah = args
    download_files(nr, localpath, filePah)

nr = 64
# copy path from the submitted jobs of train
copypaths = [
'/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852694,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852693,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852692,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852691,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852690,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852689,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852688,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852687,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852686,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852685,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852684,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852683,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852682,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852681,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852680,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852679,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852678,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852677,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852676,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852675,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852674,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852673,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852672,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852671,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852670,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852669,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852668,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852667,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852664,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852663,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852662,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852658,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852657,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852656,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852655,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852654,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852653,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852652,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852651,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852650,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852649,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852648,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852647,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852646,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852645,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852644,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852643,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852642,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852641,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852640,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852639,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852638,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852637,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852636,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852635,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852634,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852633,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852632,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852631,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852630,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852629,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852628,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852627,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852626,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852625,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852624,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852623,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852622,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852621,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852620,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852619,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852618,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852617,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852616,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852615,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852614,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852613,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852612,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852611,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852610,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852609,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852608,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852607,/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852606'    
]
# the paths that failed to merge
copypaths_faild = [
'/alice/cern.ch/user/a/alihyperloop/jobs/0185/hy_1852659']

Stage_faild = [
    'Stage_2',
]

for faild_path in copypaths_faild:
    if faild_path in copypaths:
        copypaths.remove(faild_path)

paths_sucs = get_hp_outpath(copypaths, '')

pre_paths_faild = get_hp_outpath(copypaths_faild, '')
if len(Stage_faild) == 1 and len(Stage_faild) < len(pre_paths_faild):
    Stage_faild = [Stage_faild[0]] * len(pre_paths_faild)
paths_faild = [path + '/' + stage for path in pre_paths_faild for stage in Stage_faild]

train_num = '389979'
localpath = '/media/wuct/wulby/ALICE/AnRes/D0_flow/2024/Reso'
fileName = 'AnalysisResults' # AnalysisResults or AO2D
max_workers = 32

if paths_sucs != ['']:
    down_task = [(nr, localpath + '/' + train_num + '/' + str(ipath) + '/' + fileName + '.root', path + '/' + fileName + '.root') for ipath, path in enumerate(paths_sucs)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(download_file_wrapper, down_task)

if copypaths_faild == ['']:
    sys.exit()
else:
    down_task_faild = [(nr, localpath + '/' + train_num + '/' + str(ipath + len(paths_sucs)), path + '/*' + fileName + '.root') for ipath, path in enumerate(paths_faild)]
    print(down_task_faild)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(download_file_wrapper, down_task_faild)


# for ipath, path in enumerate(paths):
#     download_files(nr, path, localpath + '/' + train_num + '/' + str(ipath), fileName)