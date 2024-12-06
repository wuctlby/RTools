import ROOT

def PrepareSamples():
    inputDataFile = ROOT.TFile("/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/ML/DATA/303753/AO2D_merged.root", "read")
    # inputDataFile = ROOT.TFile("/home/wuct/ALICE/local/DmesonAnalysis/RTools/ML/AO2D_MC_294429_medium_merge_mergedForML.root", "read")
    # dataDF = inputDataFile.Get("DF_2336986332012768")
    dataTree = inputDataFile.Get("TreeForML")

    # inputMcFile = ROOT.TFile("/home/wuct/ALICE/local/DmesonAnalysis/RTools/ML/AO2D_MC_293770_small_merge_mergedForML.root", "read")
    inputMcFile = ROOT.TFile("/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/ML/MC/AO2D_medium_304463_CombPID_merged.root", "read")
    # mcDF = inputMcFile.Get("DF_2336986331102138")
    mcTree = inputMcFile.Get("TreeForML")

    outDir = "/home/wuct/ALICE/local/DmesonAnalysis/RTools/ML/sample"
    suffix = "303753"

    pTmin = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 16]  # list
    pTmax = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 16, 24]  # list

    low_edge = [1.78, 1.78, 1.78, 1.78, 1.76, 1.76, 1.75, 1.75, 1.72, 1.72, 1.72, 1.72]
    ll_edge = [1.68, 1.68, 1.68, 1.68, 1.67, 1.67, 1.66, 1.66, 1.65, 1.65, 1.65, 1.65]
    high_edge = [1.94, 1.94, 1.94, 1.94, 1.97, 1.97, 1.97, 1.97, 2.0, 2.0, 2.0, 2.0]
    hh_edge = [2.04, 2.04, 2.04, 2.04, 2.07, 2.07, 2.07, 2.07, 2.1, 2.1, 2.1, 2.1]

    dfDataForMLApply = ROOT.RDataFrame(dataTree)
    filter = "fY > -0.8 && fY < 0.8 && fNSigTpcTofPiExpPi < 3 && fNSigTpcTofKaExpKa < 3"
    pt_mass_cut = " || ".join([f"({pTmin[i]} < fPt && fPt < {pTmax[i]} && (({ll_edge[i]} < fM && fM < {low_edge[i]}) || ({high_edge[i]} < fM && fM < {hh_edge[i]})))" for i in range(len(pTmin))])
    dfDataForMLApply.Filter(f"{filter} && ({pt_mass_cut})") \
        .Snapshot("TreeForML", f'{outDir}/DataTreeForMLTrain_{suffix}.root', 
                  [
    "fChi2PCA",
    "fCpa",
    "fCpaXY",
    "fDecayLength",
    "fDecayLengthNormalised",
    "fDecayLengthXY",
    "fDecayLengthXYNormalised",
    "fPtProng0",
    "fPtProng1",
    "fImpactParameter0",
    "fImpactParameter1",
    "fImpactParameterNormalised0",
    "fImpactParameterNormalised1",
    "fImpactParameterProduct",
    "fNSigTpcPiExpPi",
    "fNSigTpcKaExpKa",
    "fNSigTofPiExpPi",
    "fNSigTofKaExpKa",
    "fNSigTpcTofPiExpPi",
    "fNSigTpcTofKaExpKa",
    "fCosThetaStar",
    "fCt",
                   "fM", "fPt", "fY", "fCandidateSelFlag"])

    dfMcPromptForApply = ROOT.RDataFrame(mcTree)
    mc_prompt_filter = (
        "fY > -0.8 && fY < 0.8 && fOriginMcRec==1 && "
        "fNSigTpcTofPiExpPi < 3 && fNSigTpcTofKaExpKa < 3 && fCpa > 0.9 && ((fCpa > 0.9 && fPt < 5) || (fCpa > 0.92 && fPt > 5))"
    )
    dfMcPromptForApply.Filter(mc_prompt_filter) \
        .Snapshot("TreeForML", f'{outDir}/McTreeForMLPromptTrain_{suffix}.root', 
                  [
    "fChi2PCA",
    "fCpa",
    "fCpaXY",
    "fDecayLength",
    "fDecayLengthNormalised",
    "fDecayLengthXY",
    "fDecayLengthXYNormalised",
    "fPtProng0",
    "fPtProng1",
    "fImpactParameter0",
    "fImpactParameter1",
    "fImpactParameterNormalised0",
    "fImpactParameterNormalised1",
    "fImpactParameterProduct",
    "fNSigTpcPiExpPi",
    "fNSigTpcKaExpKa",
    "fNSigTofPiExpPi",
    "fNSigTofKaExpKa",
    "fNSigTpcTofPiExpPi",
    "fNSigTpcTofKaExpKa",
    "fCosThetaStar",
    "fCt",
                   "fM", "fPt", "fY", "fFlagMcMatchRec", "fOriginMcRec", "fCandidateSelFlag"])

    dfMcFDForApply = ROOT.RDataFrame(mcTree)
    dfMcFDForApply.Filter("fY > -0.8 && fY < 0.8 && fOriginMcRec==2 && fNSigTpcTofPiExpPi < 3 && fNSigTpcTofKaExpKa < 3 && ((fCpa > 0.9 && fPt < 5) || (fCpa > 0.92 && fPt > 5))") \
        .Snapshot("TreeForML", f'{outDir}/McTreeForMLFDTrain_{suffix}.root', 
                  [
    "fChi2PCA",
    "fCpa",
    "fCpaXY",
    "fDecayLength",
    "fDecayLengthNormalised",
    "fDecayLengthXY",
    "fDecayLengthXYNormalised",
    "fPtProng0",
    "fPtProng1",
    "fImpactParameter0",
    "fImpactParameter1",
    "fImpactParameterNormalised0",
    "fImpactParameterNormalised1",
    "fImpactParameterProduct",
    "fNSigTpcPiExpPi",
    "fNSigTpcKaExpKa",
    "fNSigTofPiExpPi",
    "fNSigTofKaExpKa",
    "fNSigTpcTofPiExpPi",
    "fNSigTpcTofKaExpKa",
    "fCosThetaStar",
    "fCt",
                   "fM", "fPt", "fY", "fFlagMcMatchRec", "fOriginMcRec", "fCandidateSelFlag"])

PrepareSamples()