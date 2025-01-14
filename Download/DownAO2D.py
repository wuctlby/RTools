import os
import sys
sys.path.append('../')
from utils.cook_path import get_hp_outpath


def download_files(nr, path, localpath):
    os.system(f"alien.py cp -f -T {nr} {path}/*AO2D.root file:{localpath}")

nr = 32
copypaths = [
    '/alice/cern.ch/user/a/alihyperloop/jobs/0114/hy_1144561,/alice/cern.ch/user/a/alihyperloop/jobs/0114/hy_1144562'
]

paths = get_hp_outpath(copypaths)

train_num = '322768'
localpath = '/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/ML/DATA/50100'

for ipath, path in enumerate(paths):
    download_files(nr, path, localpath + '/' + train_num + '/' + str(ipath))