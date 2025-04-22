import sys
import ROOT
from ROOT import kRed, kBlue, kGreen, kBlack, kOrange, kMagenta, kCyan, kYellow, kViolet, kTeal, kAzure, kSpring, kPink, kGray, kWhite # pylint: disable=import-error,no-name-in-module
import yaml
import argparse
sys.path.append('..')
from utils.Load import load_file, load_histos, load_runNumber


def set_frame_style(canv, particleTit, maxYaxis, minYaxis):
    canv.cd(1)
    canv.SetLeftMargin(0.20)
    canv.SetRightMargin(0.05)
    canv.SetBottomMargin(0.20)
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

def main(config_linfit, multi_trails=False):
    
    # colors = [kAzure+4, kRed+1, kGreen+4, kOrange+1, kCyan+1, kMagenta+1, kYellow+1, kTeal+1, kSpring+1, kPink+1, kGray+1, kWhite]
    
    particleTit = 'D^{0}'
    massAxisTit = '#it{M}(K#pi) (GeV/#it{c}^{2})'
    decay = "D^{0} #rightarrow K^{#minus}#pi^{+}"
    
    with open(config_linfit, 'r') as cfgLinFit:
        config = yaml.safe_load(cfgLinFit)
        
    inputFilePath = config['inputFiles']
    legTitles = config['legTitles']
    outputDir = config['outputDir']
    
    inputFiles = load_file(inputFilePath[0], 'V2VsFrac_sys', True)
    
    leg = ROOT.TLegend(0.1, 0.1, 0.9, 0.9)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(0.02)
    leg.SetTextFont(42)
    leg.SetNColumns(4)
    
    gV2VsFracs, hV2VsFracs = [], []
    hPromptV2 = []
    for iFile in range(0, len(inputFiles)):
        print(f"File {iFile}: {inputFiles[iFile]}")
        inputFile = ROOT.TFile(inputFiles[iFile], "READ")
        gV2VsFracs.append(inputFile.Get("pt_30_35/gV2VsFrac"))
        hV2VsFracs.append(inputFile.Get("pt_30_35/hV2VsFrac"))
        hPromptV2.append(inputFile.Get("hV2VsPtPrompt"))
        hPromptV2[-1].SetDirectory(0)
        hV2VsFracs[-1].SetDirectory(0)
        inputFile.Close()
    
    ouputFile = ROOT.TFile(f'{outputDir}/compare.root', 'RECREATE')
    cOut = ROOT.TCanvas("cOut", "cOut", 2400, 1200)
    cOut.Divide(2,1)
    cOut.cd(1)
    # cOut.SetGrid()
    cOut.SetTicks()
       
    sideValues, sideErrors = [], []
    for i in range(0, len(hV2VsFracs)):
        ROOT.gStyle.SetPalette(ROOT.kRainBow)
        nColors = ROOT.gStyle.GetNumberOfColors()
        colorIndex = int(i * nColors)
        color = ROOT.gStyle.GetColorPalette(colorIndex)
        hV2VsFracs[i].SetMarkerStyle(20)
        hV2VsFracs[i].SetMarkerColor(color)
        hV2VsFracs[i].SetLineColorAlpha(color, 0.1)
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
    j=0
    for i in range(0, len(gV2VsFracs)):
        # hV2VsFracs[i].Draw("same")
        # if hPromptV2[i].GetBinContent(1) <= 0 or hPromptV2[i].GetBinContent(1) > 0.3:
        #     continue
        
        # if gV2VsFracs[i].GetY()[0] < 0.1 or gV2VsFracs[i].GetY()[0] > 0.3:
        #     continue
        
        ROOT.gStyle.SetPalette(ROOT.kRainBow)
        nColors = ROOT.gStyle.GetNumberOfColors()
        colorIndex = int(i * nColors / len(gV2VsFracs))
        color = ROOT.gStyle.GetColorPalette(colorIndex)
        gV2VsFracs[i].SetMarkerStyle(20)
        if i != 2:
            gV2VsFracs[i].SetMarkerSize(1.5)
        gV2VsFracs[i].SetMarkerColor(color)
        gV2VsFracs[i].SetLineColor(color)
        linFunc = gV2VsFracs[i].GetFunction("linear")
        linFunc.SetLineColor(color)
        linFunc.SetLineStyle(1)
        # gV2VsFracs[i].Draw("p")
        linFunc.Draw("same")
        j = j+1
        legTitle = legTitles[0] + f'{j}'
        leg.AddEntry(gV2VsFracs[i], legTitle, "lp")
    
    text = ROOT.TLatex()
    text.SetNDC()
    text.SetTextSize(0.04)
    text.SetTextFont(42)
    text.DrawLatex(0.15, 0.86, f'{decay}')
    
    cOut.cd(2)
    cOut.SetTicks()
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
    parser.add_argument("--multi_trails", "-mt", action="store_true", help="use multiple trails")
    args = parser.parse_args()

    main(
        args.config_linfit,
        args.multi_trails
        
    )