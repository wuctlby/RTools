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
"/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249314,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249313,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249312,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249311,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249310,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249309,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249308,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249307,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249306,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249305,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249304,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249303,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249300,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249299,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249297,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249294,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249293,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249292,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249291,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249290,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249289,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249286,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249285,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249284,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249283,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249282,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249280,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249279,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249278,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249277,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249276,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249275,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249274,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249273,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249272,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249262,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249261,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249259,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249256,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249251,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249248,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249247,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249246,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249241,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249240,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249239,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249238,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249237,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249236,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249234,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249232,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249231,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249230,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249218,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249217,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249216,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249215,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249214,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249213,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249212,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249211,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249210,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249209,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249208,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249207,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249206,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249205,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249204,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249203,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249202,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249201,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249200,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249199,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249198,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249197,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249196,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249195,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249194,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249192,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249189,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249188,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249187,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249186,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249185,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249184,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249183,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249182,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249181,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249172,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249171,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249170,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249169,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249168,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249167,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249166,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249165,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249164,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249163,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249162,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249161,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249160,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249159,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249158,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249157,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249148,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249146,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249145,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249144,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249143,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249141,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249139,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249138,/alice/cern.ch/user/a/alihyperloop/jobs/0124/hy_1249137"
]

# the paths that failed to merge
copypaths_faild = [
    ''
]

Stage_faild = [
    ''
]

for faild_path in copypaths_faild:
    if faild_path in copypaths:
        copypaths.remove(faild_path)

paths_sucs = get_hp_outpath(copypaths, '')

pre_paths_faild = get_hp_outpath(copypaths_faild, '')
paths_faild = [path + '/' + stage for path in pre_paths_faild for stage in Stage_faild]

train_num = 'full'
localpath = '/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/ML/Results/k6080'
fileName = 'AnalysisResults' # AnalysisResults or AO2D
max_workers = 32

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