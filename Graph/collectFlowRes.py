import sys
import ROOT
import numpy as np
import argparse
sys.path.append('..')
from utils.Load import load_histos

def main(farPath):
    
    # ptmins = [1, 2, 2.5, 3, 3.5, 4, 5, 6, 7, 8, 10, 12, 16] #, 24, 36] #, 36] #14
    # ptmaxs = [2, 2.5, 3, 3.5, 4, 5, 6, 7, 8, 10, 12, 16, 24] #, 36, 50] #, 50]
    ptmins = [0.5, 1,    1.5,  2,    2.5,  3,    3.5,  4,    5,    6,    7,    8,    10,   12,   16]
    ptmaxs = [1,   1.5,  2,    2.5,  3,    3.5,  4,    5,    6,    7,    8,    10,   12,   16,   24]
    # ptmins = [1,  2,    3,    4,    5,    6,    7,    8,    12]
    # ptmaxs = [2,  3,    4,    5,    6,    7,    8,    12,   24]
    ptBinning = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 7, 8, 10, 12, 16, 24]
    # ptBinning = [1, 2, 3, 4, 5, 6, 7, 8, 12, 24]
    ptLims = list(set(ptmins + ptmaxs))
    ptLims.sort()
    print(ptLims)
    
    nPtBins = len(ptBinning) - 1
    ptBinsArr = np.asarray(ptBinning, 'd')
    print(ptBinsArr)
    ptTit = '#it{p}_{T} (GeV/#it{c})'
    
    hv2prompt = ROOT.TH1D('hv2Prompt',f';{ptTit};V2', nPtBins, ptBinsArr)
    hv2prompt.SetDirectory(0)
    hv2fd = ROOT.TH1D('hv2FD',f';{ptTit};V2', nPtBins, ptBinsArr)
    hv2fd.SetDirectory(0)
    
    # inputFiles = []
    # for ptmin, ptmax in zip(ptmins, ptmaxs):
    #     if not isinstance(ptmin, int):
    #         ptmin = str(ptmin).replace(".", "d")
    #     if not isinstance(ptmax, int):
    #         ptmax = str(ptmax).replace(".", "d")
    #     inputFiles.append(farPath + f"/cutvar_pt{ptmin}_{ptmax}/V2VsFrac/V2VsFrac_pt{ptmin}_{ptmax}.root")
    #     print(inputFiles[-1])
    
    inputFiles = [
        '/home/wuct/ALICE/local/Results/BDT/k3040/third/syst/pre_sys/cutvar_combined/V2VsFrac/V2VsFrac_combined.root',
        '/home/wuct/ALICE/local/Results/BDT/k3040/third/syst_16_24/pre_sys/cutvar_combined/V2VsFrac/V2VsFrac_combined.root'
    ]
    
    histos = load_histos(inputFiles, "hV2VsPtPrompt")
    
    # for i in range(0, len(histos)):
    #     iBin = hv2prompt.FindBin(histos[i].GetBinCenter(1))
    #     hv2prompt.SetBinContent(iBin, histos[i].GetBinContent(1))
    #     print(histos[i].GetBinContent(1))
    #     hv2prompt.SetBinError(iBin, histos[i].GetBinError(1))
    
    for iFile in range(0, nPtBins):
        # if iFile == 0:
        #     hv2prompt.SetBinContent(1, histos[0].GetBinContent(1))
        #     hv2prompt.SetBinError(1, histos[0].GetBinError(1))
        if iFile < 14:
            hv2prompt.SetBinContent(iFile + 1, histos[0].GetBinContent(iFile + 1))
            hv2prompt.SetBinError(iFile + 1, histos[0].GetBinError(iFile + 1))
        if iFile == 14:
            hv2prompt.SetBinContent(iFile + 1, histos[1].GetBinContent(1))
            hv2prompt.SetBinError(iFile + 1, histos[1].GetBinError(1))
    
    histos = load_histos(inputFiles, "hV2VsPtFD")
    
    # for i in range(0, len(histos)):
    #     iBin = hv2fd.FindBin(histos[i].GetBinCenter(1))
    #     hv2fd.SetBinContent(iBin, histos[i].GetBinContent(1))
    #     print(histos[i].GetBinContent(1))
    #     hv2fd.SetBinError(iBin, histos[i].GetBinError(1))
    
    for iFile in range(0, nPtBins):
        # if iFile == 0:
        #     hv2fd.SetBinContent(1, histos[0].GetBinContent(1))
        #     hv2fd.SetBinError(1, histos[0].GetBinError(1))
        if iFile < 14:
            hv2fd.SetBinContent(iFile + 1, histos[0].GetBinContent(iFile + 1))
            hv2fd.SetBinError(iFile + 1, histos[0].GetBinError(iFile + 1))
        if iFile == 14:
            hv2fd.SetBinContent(iFile + 1, histos[1].GetBinContent(1))
            hv2fd.SetBinError(iFile + 1, histos[1].GetBinError(1))
    
    # input("Press Enter to continue...")
    outFile = ROOT.TFile(farPath + "/V2VsPt.root", "RECREATE")
    hv2prompt.Draw('p')
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