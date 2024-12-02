#!/bin/bash

export Nr=32
export path="/alice/cern.ch/user/a/alihyperloop/jobs/0092/hy_927755/AOD"
export localpath="/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/ML/DATA/297182/755"

alien.py cp -f -T $Nr -parent 99 ${path}/*AO2D.root file:$localpath

export Nr=32
export path="/alice/cern.ch/user/a/alihyperloop/jobs/0092/hy_927754/AOD"
export localpath="/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/ML/DATA/297182/754"

alien.py cp -f -T $Nr -parent 99 ${path}/*AO2D.root file:$localpath