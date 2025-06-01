import yaml
import ROOT
import argparse

def PrepareSamples(config):
    
    # load the configuration
    with open(config, "r") as cf:
        config = yaml.safe_load(cf)
    
    inputDataName = config.get("inputDataFile", "")
    if inputDataName != "":
        dataTreeName = config['dataTree']
    inputMcName = config.get("inputMcFile", "")
    if inputMcName != "":
        mcTreeName = config['mcTree']
    
    outDir = config["outDir"]
    suffix = config["suffix"]
    
    pTmin = config["pTmins"]
    pTmax = config["pTmaxs"]
    
    low_edge = config["low_edge"]
    ll_edge = config["ll_edge"]
    high_edge = config["high_edge"]
    hh_edge = config["hh_edge"]
    
    data_filters = config.get("data_filters", [])
    mc_prompt_filters = config.get("mc_prompt_filters", [])
    mc_fd_filters = config.get("mc_fd_filters", [])
    
    # join the inv mass filters
    pt_mass_cut = " || " \
        .join([f"({pTmin[iPt]} < fPt && fPt < {pTmax[iPt]} && (({ll_edge[iPt]} < fM && fM < {low_edge[iPt]}) || ({high_edge[iPt]} < fM && fM < {hh_edge[iPt]})))" \
                for iPt in range(len(pTmin))])
    print(f'pt_mass_cut: {pt_mass_cut}')
    
    # join the filters
    if data_filters:
        data_filter = " && ".join(data_filters)
        print('data_filter: ', data_filter)
    if mc_prompt_filters:
        mc_prompt_filter = " && ".join(mc_prompt_filters)
        print('mc_prompt_filter: ', mc_prompt_filter)
    if mc_fd_filters:
        mc_fd_filter = " && ".join(mc_fd_filters)
        print('mc_fd_filter: ', mc_fd_filter)
        
    # open the input files
    if inputDataName != "":
        inputDataFile = ROOT.TFile(inputDataName, "read")
        dataTree = inputDataFile.Get(dataTreeName)
    
    if inputMcName != "":
        inputMcFile = ROOT.TFile(inputMcName, "read")
        mcTree = inputMcFile.Get(mcTreeName)
    
    if inputDataName != "":
        print('processing data')
        dfDataForMLApply = ROOT.RDataFrame(dataTree)
        dfDataForMLApply.Filter(data_filter + " && " + pt_mass_cut) \
            .Snapshot("TreeForML", f'{outDir}/DataTreeForMLTrain_{suffix}.root', [
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
                "fM", 
                "fPt", 
                "fY", 
                "fCandidateSelFlag"
                ])
    if inputMcName != "":
        if mc_prompt_filters != []:
            print('processing prompt mc')
            dfMcPromptForApply = ROOT.RDataFrame(mcTree)
            dfMcPromptForApply.Filter(mc_prompt_filter) \
                .Snapshot("TreeForML", f'{outDir}/McTreeForMLPromptTrain_{suffix}.root', [
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
                    # "fCosThetaStar",
                    # "fCt",
                    "fM", 
                    "fPt", 
                    "fY", 
                    "fFlagMcMatchRec", 
                    "fOriginMcRec", 
                    "fCandidateSelFlag"
                    ])
        if mc_fd_filters != []:
            print('processing FD mc')
            dfMcFDForApply = ROOT.RDataFrame(mcTree)
            dfMcFDForApply.Filter(mc_fd_filter) \
                .Snapshot("TreeForML", f'{outDir}/McTreeForMLFDTrain_{suffix}.root', [
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
                    # "fCosThetaStar",
                    # "fCt", 
                    "fM", 
                    "fPt", 
                    "fY", 
                    "fFlagMcMatchRec", 
                    "fOriginMcRec", 
                    "fCandidateSelFlag"
                    ])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("config", metavar="text",
                        default="config_PreSample.yml", help="the prepare sample configuration file")
    args = parser.parse_args()
    PrepareSamples(
        config=args.config
    )