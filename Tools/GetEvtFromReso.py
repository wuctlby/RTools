import sys
import ROOT
import argparse
sys.path.append('..')
from utils.Load import load_histos

def main(inputFile):

    # histos = load_histos(inputFile, "hf-task-flow-charm-hadrons/spReso/hSpResoFT0cTPCtot")

    inFile = ROOT.TFile(inputFile)
    histo2D = inFile.Get("hf-task-flow-charm-hadrons/spReso/hSpResoFT0cTPCtot")
    histo = histo2D.ProjectionX()

    totEvt = 0
    lowBin = 31
    highBin = 50
    for iBin in range(lowBin, highBin+1):
        totEvt += histo.GetBinContent(iBin)
        print(f'Bin {iBin}, Bin Center {histo.GetBinCenter(iBin)} {histo.GetBinContent(iBin)} Total events: {totEvt}')




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("inputFile", metavar="text",
                        default="an_res.root", help="input ROOT file")
    args = parser.parse_args()

    main(
        inputFile=args.inputFile
        )