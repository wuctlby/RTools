import sys
import ROOT
import argparse
sys.path.append('..')
from utils.Load import load_histos

def main(inputFile, output):

    # histos = load_histos(inputFile, "hf-task-flow-charm-hadrons/spReso/hSpResoFT0cTPCtot")

    inFile = ROOT.TFile(inputFile)
    histo2D = inFile.Get("FT0c_FV0a_TPCtot/hSpResoFT0cFV0a")
    histo = histo2D.ProjectionX()
    histo.SetDirectory(0)

    totEvt = 0
    lowBin = 31
    highBin = 50
    for iBin in range(lowBin, highBin+1):
        totEvt += histo.GetBinContent(iBin)
        print(f'Bin {iBin}, Bin Center {histo.GetBinCenter(iBin)} {histo.GetBinContent(iBin)} Total events: {totEvt}')

    hEvt = ROOT.TH1F("hEvtDistribution", "Event Distribution", 90, 0, 90)
    hEvt.SetDirectory(0)
    for iBin in range(1, histo.GetNbinsX()+1):
        hEvt.SetBinContent(iBin, histo.GetBinContent(iBin))
    hEvt.SetName("hEvtDistribution")
    hEvt.SetTitle("Event Distribution")
    outFile = ROOT.TFile(output + "EvtDistribution_2023.root", "RECREATE")
    hEvt.Write()
    histo.Write()
    outFile.Close()
    inFile.Close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("inputFile", metavar="text",
                        default="an_res.root", help="input ROOT file")
    parser.add_argument("--output", '-o', metavar="text", required=False,
                        default="./Event", help="output file path")
    args = parser.parse_args()

    main(
        inputFile=args.inputFile,
        output=args.output
        )