import sys
import ROOT
import numpy as np
import argparse
sys.path.append('..')
from utils.Load import load_histos

def main(farPath):
    
    ptmins = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12]  # list
    ptmaxs =  [2, 3, 4, 5, 6, 7, 8, 10, 12, 16]  # list
    
    ptLims = list(ptmins)
    nPtBins = len(ptmins)
    ptLims.append(ptmaxs[-1])
    ptBinsArr = np.asarray(ptLims, 'd')
    ptTit = '#it{p}_{T} (GeV/#it{c})'
    
    hv2prompt = ROOT.TH1D('hv2Prompt',f';{ptTit};V2', nPtBins, ptBinsArr)
    hv2prompt.SetDirectory(0)
    hv2fd = ROOT.TH1D('hv2FD',f';{ptTit};V2', nPtBins, ptBinsArr)
    hv2fd.SetDirectory(0)
    
    inputFiles = []
    for ptmin, ptmax in zip(ptmins, ptmaxs):
        inputFiles.append(farPath + f"/cutvar_pt{ptmin}_{ptmax}/V2VsFrac/V2VsFrac_pt{ptmin}_{ptmax}.root")
        print(inputFiles[-1])
    
    histos = load_histos(inputFiles, "hV2VsPtPrompt")
    
    for i in range(0, len(histos)):
        hv2prompt.SetBinContent(i+1, histos[i].GetBinContent(1))
        print(histos[i].GetBinContent(1))
        hv2prompt.SetBinError(i+1, histos[i].GetBinError(1))
        
    histos = load_histos(inputFiles, "hV2VsPtFD")
    
    for i in range(0, len(histos)):
        hv2fd.SetBinContent(i+1, histos[i].GetBinContent(1))
        print(histos[i].GetBinContent(1))
        hv2fd.SetBinError(i+1, histos[i].GetBinError(1))
        
    # input("Press Enter to continue...")
    outFile = ROOT.TFile(farPath + "/V2VsPt.root", "RECREATE")
    hv2prompt.Write()
    hv2fd.Write()
    outFile.Close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("farPath", metavar="text",
                        default="path/to/cutvar", help="the father cutcar path")
    args = parser.parse_args()

    main(
        farPath=args.farPath
    )