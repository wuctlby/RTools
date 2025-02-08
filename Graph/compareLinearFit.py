import sys
import ROOT
from ROOT import kRed, kBlue, kGreen, kBlack, kOrange, kMagenta, kCyan, kYellow, kViolet, kTeal, kAzure, kSpring, kPink, kGray, kWhite # pylint: disable=import-error,no-name-in-module
import yaml
import argparse
sys.path.append('..')
from utils.Load import load_histos

def set_frame_style(canv, particleTit, maxYaxis, minYaxis):
    canv.SetLeftMargin(0.15)
    canv.SetRightMargin(0.05)
    canv.SetBottomMargin(0.15)
    canv.SetTopMargin(0.05)
    hFrame = canv.DrawFrame(0.0, minYaxis, 1, maxYaxis, f";Non-prompt {particleTit} fraction; #it{{v}}_{{2}}^{{#it{{obs}}}}")
    hFrame.GetYaxis().SetDecimals()
    hFrame.GetYaxis().SetNoExponent()
    hFrame.GetXaxis().SetMoreLogLabels()
    hFrame.GetYaxis().SetTitleSize(0.04)
    hFrame.GetYaxis().SetTitleOffset(1.4)
    hFrame.GetYaxis().SetLabelSize(0.04)
    hFrame.GetXaxis().SetTitleSize(0.04)
    hFrame.GetXaxis().SetLabelSize(0.04)
    hFrame.GetXaxis().SetTitleOffset(1.4)
    hFrame.GetYaxis().SetNdivisions(505)

def main(config_linfit):
    
    colors = [kAzure+4, kRed+1, kGreen+4, kOrange+1, kCyan+1, kMagenta+1, kYellow+1, kTeal+1, kSpring+1, kPink+1, kGray+1, kWhite]
    
    particleTit = 'D^{0}'
    massAxisTit = '#it{M}(K#pi) (GeV/#it{c}^{2})'
    decay = "D^{0} #rightarrow K^{#minus}#pi^{+}"
    
    with open(config_linfit, 'r') as cfgLinFit:
        config = yaml.safe_load(cfgLinFit)
        
    inputFiles = config['inputFiles']
    legTitles = config['legTitles']
    outputDir = config['outputDir']
    
    
    leg = ROOT.TLegend(0.15, 0.15, 0.35, 0.35)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(0.045)
    leg.SetTextFont(42)
    leg.SetNColumns(1)
    
    gV2VsFracs, hV2VsFracs = [], []
    for iFile in range(0, len(inputFiles)):
        print(f"File {iFile}: {inputFiles[iFile]}")
        inputFile = ROOT.TFile(inputFiles[iFile], "READ")
        gV2VsFracs.append(inputFile.Get("Graph"))
        hV2VsFracs.append(inputFile.Get("hV2VsFrac_0"))
        hV2VsFracs[-1].SetDirectory(0)
        inputFile.Close()
    
    ouputFile = ROOT.TFile(f'{outputDir}/compare.root', 'RECREATE')
    cOut = ROOT.TCanvas("cOut", "cOut", 1200, 1200)
    # cOut.SetGrid()
    cOut.SetTicks()
       
    sideValues, sideErrors = [], []
    for i in range(0, len(hV2VsFracs)):
        hV2VsFracs[i].SetMarkerStyle(20)
        hV2VsFracs[i].SetMarkerColor(colors[i])
        hV2VsFracs[i].SetLineColorAlpha(colors[i], 0.1)
        maxBin = hV2VsFracs[i].GetNbinsX()
        sideValues.append(hV2VsFracs[i].GetBinContent(1))
        sideValues.append(hV2VsFracs[i].GetBinContent(maxBin))
        sideErrors.append(hV2VsFracs[i].GetBinError(1))
        sideErrors.append(hV2VsFracs[i].GetBinError(maxBin))

    maxYaxis = max(sideValues) + max(sideErrors)
    minYaxis = min(sideValues) - max(sideErrors)
    print(f"maxYaxis: {maxYaxis}, minYaxis: {minYaxis}")
    if minYaxis < 0:
        minYaxis = minYaxis*1.5
    set_frame_style(cOut, particleTit, maxYaxis*1.2, minYaxis)
    
    for i in range(0, len(gV2VsFracs)):
        hV2VsFracs[i].Draw("same")
        gV2VsFracs[i].SetMarkerStyle(20)
        if i != 2:
            gV2VsFracs[i].SetMarkerSize(1.5)
        gV2VsFracs[i].SetMarkerColor(colors[i])
        gV2VsFracs[i].SetLineColor(colors[i])
        linFunc = gV2VsFracs[i].GetFunction("linear")
        linFunc.SetLineColor(colors[i])
        linFunc.SetLineStyle(9-i)
        gV2VsFracs[i].Draw("p")
        # linFunc.Draw("same")
        leg.AddEntry(gV2VsFracs[i], legTitles[i], "lp")
    
    text = ROOT.TLatex()
    text.SetNDC()
    text.SetTextSize(0.04)
    text.SetTextFont(42)
    text.DrawLatex(0.15, 0.96, f'{decay}')
    
    leg.Draw()
    # cOut.BuildLegend(0.15, 0.15, 0.35, 0.35)
    cOut.Update()

    cOut.Draw()
    cOut.SaveAs(f'{outputDir}/compare.pdf')
    input("Press Enter to continue...")
    
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("config_linfit", metavar="text",
                        default="config_linfit.yml", help="the configuration file")
    args = parser.parse_args()

    main(
        args.config_linfit
    )