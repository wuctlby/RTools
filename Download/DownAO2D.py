import os
import sys
import concurrent.futures
sys.path.append('../')
from utils.cook_path import get_hp_outpath


def download_files(nr, localpath, filePah):
    os.system(f"alien.py cp -f -T {nr} {filePah} file:{localpath}")
    
def download_file_wrapper(args):
    nr, localpath, filePah = args
    download_files(nr, localpath, filePah)

nr = 64
# copy path from the submitted jobs of train
copypaths = [
    '/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164175,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164174,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164173,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164172,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164171,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164170,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164169,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164168,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164167,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164166,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164165,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164164,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164163,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164162,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164161,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164160,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164159,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164158,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164157,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164156,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164155,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164154,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164153,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164152,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164151,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164150,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164149,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164148,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164147,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164146,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164145,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164144,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164143,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164142,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164141,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164140,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164139,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164138,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164137,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164136,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164135,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164133,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164132,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164130,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164129,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164128,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164127,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164126,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164124,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164123,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164120,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164119,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164118,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163958,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163954,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163950,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163945,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163944,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163941,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163930,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163929,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163928,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163927,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163926,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163925,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163924,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163923,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163909,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163908,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163907,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163906,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163905,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163904,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163903,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163902,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163901,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163900,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163899,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163898,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163897,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163896,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163895,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163894,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163893,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163892,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163891,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163890,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163889,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163888,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163887,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163885,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163873,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163872,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163858,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163857,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163856,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163855,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163854,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163853,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163852,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163851,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163850,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163849,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163848,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163847,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163846,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163845,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163844,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163843,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163842,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163841,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163840,/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1163839'
]

# the paths that failed to merge
copypaths_faild = [
    '/alice/cern.ch/user/a/alihyperloop/jobs/0116/hy_1164168'
]

Stage_faild = [
    'Stage_1'
]

for faild_path in copypaths_faild:
    if faild_path in copypaths:
        copypaths.remove(faild_path)

paths_sucs = get_hp_outpath(copypaths, '')

pre_paths_faild = get_hp_outpath(copypaths_faild, '')
paths_faild = [path + '/' + stage for path in pre_paths_faild for stage in Stage_faild]

train_num = '324130'
localpath = '/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/ML/Results'
fileName = 'AnalysisResults' # AnalysisResults or AO2D
max_workers = 32

down_task = [(nr, localpath + '/' + train_num + '/' + str(ipath) + '/' + fileName + '.root', path + '/' + fileName + '.root') for ipath, path in enumerate(paths_sucs)]
with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    executor.map(download_file_wrapper, down_task)
    
down_task_faild = [(nr, localpath + '/' + train_num + '/' + str(ipath + len(paths_sucs)), path + '/*' + fileName + '.root') for ipath, path in enumerate(paths_faild)]
print(down_task_faild)
with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    executor.map(download_file_wrapper, down_task_faild)


# for ipath, path in enumerate(paths):
#     download_files(nr, path, localpath + '/' + train_num + '/' + str(ipath), fileName)