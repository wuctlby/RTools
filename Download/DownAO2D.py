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
    '/alice/cern.ch/user/a/alihyperloop/jobs/0180/hy_1801720'
    
]
# the paths that failed to merge
copypaths_faild = [
  '/alice/cern.ch/user/a/alihyperloop/jobs/0180/hy_1801944'
]

Stage_faild = [
    'Stage_1',
]

for faild_path in copypaths_faild:
    if faild_path in copypaths:
        copypaths.remove(faild_path)

paths_sucs = get_hp_outpath(copypaths, '')

pre_paths_faild = get_hp_outpath(copypaths_faild, '')
paths_faild = [path + '/' + stage for path in pre_paths_faild for stage in Stage_faild]

train_num = '384760g'
localpath = '/home/wuct/xxf-files'
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