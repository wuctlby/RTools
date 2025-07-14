import os
import yaml
import ROOT
import argparse

def PrepareSamples(config):
    
    # load the configuration
    if not isinstance(config, dict):
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
    
    low_edge = config.get("low_edge", [])
    ll_edge = config["ll_edge"]
    high_edge = config.get("high_edge", [])
    hh_edge = config["hh_edge"]
    
    data_filters = config.get("data_filters", [])
    mc_prompt_filters = config.get("mc_prompt_filters", [])
    mc_fd_filters = config.get("mc_fd_filters", [])
    
    os.makedirs(outDir, exist_ok=True)

    # join the inv mass filters
    if len(low_edge) == 0 and len(high_edge) == 0:
        pt_mass_cut = " || ".join([f"({pTmin[iPt]} < fPt && fPt < {pTmax[iPt]} && ({ll_edge[iPt]} < fM && fM < {hh_edge[iPt]}))" \
                                    for iPt in range(len(pTmin))])
    else:
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
        print(f'inputDataFile: {inputDataFile.GetName()}')
        print(f'dataTreeName: {dataTreeName}')
        print(f'outDir: {outDir}')
        print(f'type(dataTreeName): {type(dataTreeName)}')
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
                # "fCt",
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
                    "fCosThetaStar",
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
                    "fCosThetaStar",
                    # "fCt", 
                    "fM", 
                    "fPt", 
                    "fY", 
                    "fFlagMcMatchRec", 
                    "fOriginMcRec", 
                    "fCandidateSelFlag"
                    ])

def PrepareSamples_multi(config):
    with open(config, 'r') as file:
        config = yaml.safe_load(file)

    inputDataName = config.get("inputDataFile", '')
    inputMcName = config.get("inputMcFile", '')
    
    if inputDataName != "":
        configs = []
        inputDataFiles = []
        for root, _, files in os.walk(inputDataName):
            found_files = [os.path.join(root, name) for name in files if name.endswith('_tableMerged.root')]
            inputDataFiles.extend(found_files)
        if len(inputDataFiles) == 0:
            print("No data files found.")
        else:
            print(f"Found {len(inputDataFiles)} data files.")
            for inputDataFile in inputDataFiles:
                print(f"Processing data file: {inputDataFile}")
                config['inputDataFile'] = inputDataFile
                config['inputMcFile'] = ""
                config['outDir'] = os.path.dirname(inputDataFile)
                configs.append(config.copy())
            for i in range(0, len(configs), 5):
                chunk = configs[i:i+5]
                multiprocess(PrepareSamples, [chunk], max_workers=5)
                print(f"Processed chunk {i//5 + 1}/{(len(inputDataFiles) + 5 - 1) // 5}")

    if inputMcName != "":
        configs = []
        inputMcFiles = []
        for root, _, files in os.walk(inputMcName):
            found_files = [os.path.join(root, name) for name in files if name.endswith('_tableMerged.root')]
            inputMcFiles.extend(found_files)
        if len(inputMcFiles) == 0:
            print("No MC files found.")
        else:
            print(f"Found {len(inputMcFiles)} MC files.")
            for inputMcFile in inputMcFiles:
                print(f"Processing MC file: {inputMcFile}")
                config['inputMcFile'] = inputMcFile
                config['inputDataFile'] = ""
                config['outDir'] = os.path.dirname(inputMcFile)
                configs.append(config.copy())
            for i in range(0, len(configs), 5):
                chunk = configs[i:i+5]
                multiprocess(PrepareSamples, [chunk], max_workers=5)

def multiprocess(func, args, max_workers=4):
    import multiprocessing
    try:
        pool = multiprocessing.Pool(processes=max_workers)
        results = pool.starmap(func, zip(*args))
        
        flat_results = []
        for result in results:
            if isinstance(result, list):
                flat_results.extend(result)
            else:
                flat_results.append(result)
        return flat_results
    except Exception as e:
        print(f"Error in process pool: {e}")
        raise
    finally:
        pool.close()
        pool.join()
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("config", metavar="text",
                        default="config_PreSample.yml", help="the prepare sample configuration file")
    parser.add_argument("--multifile", '-m', action="store_true",
                        help="process multiple files in the input")
    args = parser.parse_args()
    if args.multifile:
        print("Processing multiple files...")
        PrepareSamples_multi(
            config=args.config
        )
    else:
        PrepareSamples(
            config=args.config
        )