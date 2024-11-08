import ROOT

def PrepareSamples():
    inputDataFile = ROOT.TFile("/media/wuct/wulby/ALICE/AO2D/PASS4/DATA/AO2D_DATA_PASS4.root", "read")
    dataDF = inputDataFile.Get("DF_2336960459658208")
    dataTree = dataDF.Get("O2hfcandd0lite")

    inputMcFile = ROOT.TFile("/media/wuct/wulby/ALICE/AO2D/PASS4/MC/AO2D_285404.root", "read")
    mcDF = inputMcFile.Get("DF_2336986331102138")
    mcTree = mcDF.Get("O2hfcandd0lite")

    dfDataForMLApply = ROOT.RDataFrame(dataTree)
    dfDataForMLApply.Filter("fY > -0.8 && fY < 0.8 && fM <1.8 or fM > 1.95") \
        .Snapshot("TreeML", "./DataTreeForMLTrain.root", 
                  ["fCpa", "fCpaXY", 
                   "fDecayLength", "fDecayLengthXY", "fDecayLengthNormalised", "fDecayLengthXYNormalised",
                   "fMaxNormalisedDeltaIP", "fImpactParameter0", "fImpactParameter1", "fImpactParameterNormalised0", "fImpactParameterNormalised1", "fImpactParameterProduct",
                   "fNSigTpcPi0", "fNSigTpcPi1", "fNSigTpcKa0", "fNSigTpcKa1",
                   "fNSigTofPi0", "fNSigTofPi1", "fNSigTofKa0", "fNSigTofKa1",
                   "fNSigTpcTofPi0", "fNSigTpcTofPi1", "fNSigTpcTofKa0", "fNSigTpcTofKa1",
                   "fM", "fPt", "fY", "fFlagMc", "fOriginMcRec", "fCandidateSelFlag"])

    dfMcPromptForApply = ROOT.RDataFrame(mcTree)
    dfMcPromptForApply.Filter("fY > -0.8 && fY < 0.8 && fOriginMcRec==1") \
        .Snapshot("TreeML", "./McTreeForMLPromptTrain.root", 
                  ["fCpa", "fCpaXY", 
                   "fDecayLength", "fDecayLengthXY", "fDecayLengthNormalised", "fDecayLengthXYNormalised",
                   "fMaxNormalisedDeltaIP", "fImpactParameter0", "fImpactParameter1", "fImpactParameterNormalised0", "fImpactParameterNormalised1", "fImpactParameterProduct",
                   "fNSigTpcPi0", "fNSigTpcPi1", "fNSigTpcKa0", "fNSigTpcKa1",
                   "fNSigTofPi0", "fNSigTofPi1", "fNSigTofKa0", "fNSigTofKa1",
                   "fNSigTpcTofPi0", "fNSigTpcTofPi1", "fNSigTpcTofKa0", "fNSigTpcTofKa1",
                   "fM", "fPt", "fY", "fFlagMc", "fOriginMcRec", "fCandidateSelFlag"])

    dfMcFDForApply = ROOT.RDataFrame(mcTree)
    dfMcFDForApply.Filter("fY > -0.8 && fY < 0.8 && fOriginMcRec==2") \
        .Snapshot("TreeML", "./McTreeForMLFDTrain.root", 
                  ["fCpa", "fCpaXY", 
                   "fDecayLength", "fDecayLengthXY", "fDecayLengthNormalised", "fDecayLengthXYNormalised",
                   "fMaxNormalisedDeltaIP", "fImpactParameter0", "fImpactParameter1", "fImpactParameterNormalised0", "fImpactParameterNormalised1", "fImpactParameterProduct",
                   "fNSigTpcPi0", "fNSigTpcPi1", "fNSigTpcKa0", "fNSigTpcKa1",
                   "fNSigTofPi0", "fNSigTofPi1", "fNSigTofKa0", "fNSigTofKa1",
                   "fNSigTpcTofPi0", "fNSigTpcTofPi1", "fNSigTpcTofKa0", "fNSigTpcTofKa1",
                   "fM", "fPt", "fY", "fFlagMc", "fOriginMcRec", "fCandidateSelFlag"])

    return 0

PrepareSamples()