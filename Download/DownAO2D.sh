#!/bin/bash

export Nr=32
export path="/alice/cern.ch/user/a/alihyperloop/jobs/0099/hy_990507"
export localpath="/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/ML/Results/304024/7"

alien.py cp -f -T $Nr ${path}/*AnalysisResults.root file:$localpath

export Nr=32
export path="/alice/cern.ch/user/a/alihyperloop/jobs/0099/hy_990506"
export localpath="/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/ML/Results/304024/6"

alien.py cp -f -T $Nr ${path}/*AnalysisResults.root file:$localpath

export Nr=32
export path="/alice/cern.ch/user/a/alihyperloop/jobs/0099/hy_990505"
export localpath="/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/ML/Results/304024/5"

alien.py cp -f -T $Nr ${path}/*AnalysisResults.root file:$localpath

export Nr=32
export path="/alice/cern.ch/user/a/alihyperloop/jobs/0099/hy_990504"
export localpath="/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/ML/Results/304024/4"

alien.py cp -f -T $Nr ${path}/*AnalysisResults.root file:$localpath

export Nr=32
export path="/alice/cern.ch/user/a/alihyperloop/jobs/0099/hy_990503"
export localpath="/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/ML/Results/304024/3"

alien.py cp -f -T $Nr ${path}/*AnalysisResults.root file:$localpath

export Nr=32
export path="/alice/cern.ch/user/a/alihyperloop/jobs/0099/hy_990502"
export localpath="/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/ML/Results/304024/2"

alien.py cp -f -T $Nr ${path}/*AnalysisResults.root file:$localpath

export Nr=32
export path="/alice/cern.ch/user/a/alihyperloop/jobs/0099/hy_990501"
export localpath="/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/ML/Results/304024/1"

alien.py cp -f -T $Nr ${path}/*AnalysisResults.root file:$localpath

export Nr=32
export path="/alice/cern.ch/user/a/alihyperloop/jobs/0099/hy_990500"
export localpath="/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/ML/Results/304024/0"

alien.py cp -f -T $Nr ${path}/*AnalysisResults.root file:$localpath

export Nr=32
export path="/alice/cern.ch/user/a/alihyperloop/jobs/0098/hy_983950/AOD"
export localpath="/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/ML/DATA/303753/1"

alien.py cp -f -T $Nr ${path}/*AO2D.root file:$localpath

export Nr=32
export path="/alice/cern.ch/user/a/alihyperloop/jobs/0098/hy_983949/AOD"
export localpath="/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/ML/DATA/303753/0"

alien.py cp -f -T $Nr ${path}/*AO2D.root file:$localpath

