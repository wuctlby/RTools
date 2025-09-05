import os
import sys
import ROOT
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, '..'))
from utils.Load import load_file, load_histos, load_runNumber
from utils.compute import compute_ratio_histo


def compare(histoNames):
    cList = []
    for histoName in histoNames:
        cList.append(ROOT.TCanvas(histoName, histoName, 2000, 1600))
        # load histograms
        inHistos = load_histos(inputFiles, histoName)

        for i, histo in enumerate(inHistos):
            histo.SetLineColor(i+2)
            if i == 0:
                histo.Draw()
            else:
                histo.Draw("same")

        cList[-1].Draw()

def compare_multi(histoNames, inputFiles):
    cList = []
    inHistos = []
    runNumber = ['high', 'low', 'med', 'int']
    # runNumber = load_runNumber(inputFiles)
    for iFile, histoName in enumerate(histoNames):
        cList.append(ROOT.TCanvas(histoName, 'Resolution', 1600, 1200))
        cList[-1].Divide(2, 1)
        cList[-1].cd(1).SetPad(0.0, 0.0, 0.7, 1.0)
        cList[-1].cd(2).SetPad(0.65, 0.0, 1.0, 1.0)
        # runNumber.append(iFile)
        # Create legend
        leg = ROOT.TLegend(0.1, 0.1, 0.9, 0.9)
        leg.SetHeader("Run List")
        leg.SetNColumns(4)
        leg.SetBorderSize(0)
        leg.SetTextSize(0.04)

        # Latex 
        latex = ROOT.TLatex()
        latex.SetNDC()
        latex.SetTextSize(0.04)
        latex.SetTextFont(42)


        # Draw histograms on the left pad
        cList[-1].cd(1)
        # inHistos = load_histos(inputFiles, histoName)
        for iF, inputFile in enumerate(inputFiles):
            file = ROOT.TFile(inputFile)
            print(inputFile)
            inHistos.append(file.Get(histoName))
            inHistos[-1].SetDirectory(0)
        
        # if len(inHistos) != len(runNumber):
        #     print(inputFiles)
        #     print(runNumber)
        #     print("Error: Number of histograms and run numbers do not match")
        #     return

        for i, histo in enumerate(inHistos):

            ROOT.gStyle.SetPalette(ROOT.kRainBow)
            nColors = ROOT.gStyle.GetNumberOfColors()
            colorIndex = int(i * nColors / len(inHistos))
            color = ROOT.gStyle.GetColorPalette(colorIndex)

            histo.SetLineColor(color)
            histo.SetXTitle("centrality (%)")
            histo.SetYTitle("#it{R}_{2} {SP}")
            histo.GetYaxis().SetTitleOffset(1)
            histo.GetYaxis().SetTitleSize(0.05)
            histo.GetYaxis().SetRangeUser(0., 1.)
            histo.SetTitle("")
            leg.AddEntry(histo, runNumber[i], "l")
            if i == 0:
                histo.Draw()
            else:
                histo.Draw("same")
        latex.DrawLatex(0.1, 0.92, histoName.split('/')[0])

        # Draw legend on the right pad
        cList[-1].cd(2)
        leg.Draw()

        cList[-1].Update()

        input("Press Enter to continue...")

        outputName = histoName.split('/')[-1]
        if iFile % 2 == 0:
            pdfSuffix = '('
        elif iFile % 2 == 1:
            pdfSuffix = ')'
        cList[-1].SaveAs(f'./{outputName}_k3050.pdf{pdfSuffix}')
        # outFile = ROOT.TFile(f'./{outputName}_k3050.root', 'RECREATE')
        # cList[-1].Write()

def doRato(inputFiles, histoNames):
    cList = []
    subInputFiles = inputFiles[1:]
    runNumber = ['high', 'low', 'med']
    for iFile, histoName in enumerate(histoNames):
        # load histograms
        inHistos = load_histos(inputFiles, histoName)

        ratioHistos = compute_ratio_histo(inHistos)

        cList.append(ROOT.TCanvas(histoName, 'Resolution', 3200, 2600))
        cList[-1].Divide(2, 1)
        cList[-1].cd(1).SetPad(0.0, 0.0, 0.7, 1.0)
        cList[-1].cd(2).SetPad(0.65, 0.0, 1.0, 1.0)
        
        # Create legend
        leg = ROOT.TLegend(0.1, 0.1, 0.9, 0.9)
        leg.SetHeader("Run List")
        leg.SetNColumns(4)
        leg.SetBorderSize(0)
        leg.SetTextSize(0.04)

        # Latex 
        latex = ROOT.TLatex()
        latex.SetNDC()
        latex.SetTextSize(0.04)
        latex.SetTextFont(42)


        # Draw histograms on the left pad
        cList[-1].cd(1)
        # if len(ratioHistos) != len(runNumber):
        #     print(inputFiles)
        #     print(runNumber)
        #     print("Error: Number of histograms and run numbers do not match")
        #     return

        for i, ratioHisto in enumerate(ratioHistos):

            ROOT.gStyle.SetPalette(ROOT.kRainBow)
            nColors = ROOT.gStyle.GetNumberOfColors()
            colorIndex = int(i * nColors / len(inHistos))
            color = ROOT.gStyle.GetColorPalette(colorIndex)

            ratioHisto.SetLineColor(color)
            ratioHisto.SetXTitle("centrality (%)")
            ratioHisto.SetYTitle("Ratio to Intergrated")
            ratioHisto.GetYaxis().SetTitleOffset(1)
            ratioHisto.GetYaxis().SetTitleSize(0.05)
            ratioHisto.GetYaxis().SetRangeUser(0.95, 1.05)
            ratioHisto.SetTitle("")
            leg.AddEntry(ratioHisto, runNumber[i], "l")
            if i == 0:
                ratioHisto.Draw()
            else:
                ratioHisto.Draw("same")
            
            if 'delta_cent' in histoName:
                ratio = ratioHisto.GetBinContent(1)
                if ratio < 0.99:
                    print(f'RunNmber: {runNumber[i]}')
                    print(f'Ratio: {ratio}')
        latex.DrawLatex(0.1, 0.92, histoName.split('/')[0])

        # Draw legend on the right pad
        cList[-1].cd(2)
        leg.Draw()

        cList[-1].Update()

        # input("Press Enter to continue...")

        outputName = histoName.split('/')[-1]
        if iFile % 2 == 0:
            pdfSuffix = '('
        elif iFile % 2 == 1:
            pdfSuffix = ')'
        cList[-1].SaveAs(f'./{outputName}_ratio_k3050.pdf{pdfSuffix}')

# configuration
inFilePath = '/home/wuct/ALICE/local/dev/d0_v2/test/T01/pass4Wpass5Corr'
keyWord = 'reso'

histoNames = [
    "FT0c_FV0a_TPCtot/histo_reso",
    "FT0c_FV0a_TPCtot/histo_reso_delta_cent",
    ]

# load files
# inputFile_int = load_file("/media/wuct/wulby/ALICE/AnRes/resolution/output_reso", 'k3050_inte')
# inFilePath = [
#     "/home/wuct/ALICE/local/reso/DmesonAnalysis/run3/flow/reso/Results/0100/k0100/large/sp/resolution/resosp0100l_hig_occu_Reso.root",
#     "/home/wuct/ALICE/local/reso/DmesonAnalysis/run3/flow/reso/Results/0100/k0100/large/sp/resolution/resosp0100l_low_occu_Reso.root",
#     "/home/wuct/ALICE/local/reso/DmesonAnalysis/run3/flow/reso/Results/0100/k0100/large/sp/resolution/resosp0100l_med_occu_Reso.root"
# ]
inputFiles = load_file(inFilePath, keyWord)

compare_multi(histoNames, inputFiles)
# inputFile_int = '/home/wuct/ALICE/local/dev/d0_v2/test/T01/pass4Wpass5Corr/reso_resospprivate.root'
# # doratio
# inputFiles = inputFile_int + inputFiles

# doRato(inputFiles, histoNames)
