import yaml
import argparse
import sys
from ROOT import TCanvas, TFile, TLegend, TGaxis, TGraph, TGraphAsymmErrors, TLatex, TLine # pylint: disable=import-error,no-name-in-module
from ROOT import gROOT, gPad, kGreen, kBlack, kRed, kAzure, kGray, kOrange, kMagenta, kBlue, kCyan, kSpring # pylint: disable=import-error,no-name-in-module
from ROOT import kFullCircle, kFullSquare, kOpenCircle, kOpenSquare, kOpenTriangleUp, kOpenTriangleDown, kOpenDiamond, kOpenCross, kOpenStar, kOpenStar, kOpenStar, kOpenStar, kOpenStar # pylint: disable=import-error,no-name-in-module

sys.path.append('../../')
from utils.StyleFormatter import SetGlobalStyle, SetObjectStyle, DivideCanvas

def getCorrError(deltaNum, deltaDen, Num, Den):
    error = Num / Den * (deltaNum / Num - deltaDen / Den)
    return error
### Occupancy resolution
# inputFileNames = [
#     '/home/wuct/localAnalysis/flow/dev/DmesonAnalysis/run3/flow/Results/2060/k3050/small/sp/ry/raw_yields3050s_occ_inte.root',
#     '/home/wuct/localAnalysis/flow/dev/DmesonAnalysis/run3/flow/Results/2060/k3050/small/sp/ry/raw_yields3050s_occ_high.root',
#     '/home/wuct/localAnalysis/flow/dev/DmesonAnalysis/run3/flow/Results/2060/k3050/small/sp/ry/raw_yields3050s_occ_mid.root',
#     '/home/wuct/localAnalysis/flow/dev/DmesonAnalysis/run3/flow/Results/2060/k3050/small/sp/ry/raw_yields3050s_occ_low.root',
#     '/home/wuct/localAnalysis/flow/dev/DmesonAnalysis/run3/flow/Results/2060/k3050/small/sp/ry/raw_yields3050s_occ_inte_eq.root',
#     '/home/wuct/localAnalysis/flow/dev/DmesonAnalysis/run3/flow/Results/2060/k3050/small/sp/ry/raw_yields3050s_pass3_ori.root'
# ]
# histNames = ['hvnSimFit', 'hvnSimFit', 'hvnSimFit', 'hvnSimFit', 'hvnSimFit', 'hvnSimFit']
# iRefFile = 0

inputFileNames = [ '/home/wuct/ALICE/local/DmesonAnalysis/run3/flow/Results/2060/k3050/small/sp/resolution/resosp3050s_291131_inte_gain_Reso.root',
                  '/home/wuct/ALICE/local/DmesonAnalysis/run3/flow/Results/2060/k3050/medium/sp/resolution/resosp3050m_293294_med_inte_gain_Reso.root']
histPaths = 'FT0c_FV0a_TPCtot'
histNames = ['histo_reso', 'histo_reso']
iRefFile = 0

# Load input files
histos = []
for iFile, file in enumerate(inputFileNames):
    inputFile = TFile(f'{file}', 'r')
    if histPaths == '':
        hist = inputFile.Get(histNames[iFile])
    else:
        hist = inputFile.Get(f'{histPaths}/{histNames[iFile]}')
        print(hist)
    if hist == None:
        print(f'Cannot find {histPaths}/{histNames[iFile]} in {file}')
        sys.exit(1)
    print(str(type(hist)).split('.')[-1].split(' ')[0])
    if str(type(hist)).split('.')[-1].split(' ')[0] != 'TGraphAsymmErrors':
        hist.SetDirectory(0)
    histos.append(hist)

# Get difference
nPoints = histos[iRefFile].GetNbinsX()
absDiff, relDiff = {i: [] for i in range(len(histos))}, {i: [] for i in range(len(histos))}
errRelDiff, errAbsDiff = {i: [] for i in range(len(histos))}, {i: [] for i in range(len(histos))}

for ihist, hist in enumerate(histos):
    if ihist != iRefFile:
        for iPoint in range(1, nPoints + 1):
            # Get difference
            absDiff[ihist].append(histos[ihist].GetBinContent(iPoint) - histos[iRefFile].GetBinContent(iPoint))
            relDiff[ihist].append(histos[ihist].GetBinContent(iPoint) / histos[iRefFile].GetBinContent(iPoint))

            # Get error
            errAbsDiff[ihist].append(
                abs(histos[ihist].GetBinError(iPoint) - histos[iRefFile].GetBinError(iPoint))
            )
            errRelDiff[ihist].append(
                getCorrError(histos[ihist].GetBinError(iPoint), histos[iRefFile].GetBinError(iPoint),
                             histos[ihist].GetBinContent(iPoint), histos[iRefFile].GetBinContent(iPoint))
            )
    else:
        continue

# set style
colors = [kBlack, kRed+1, kAzure+4,kGreen+2, kOrange+7, kMagenta+1, kBlue, kCyan+3, kSpring-5, kMagenta+1, kBlue, kCyan+3, kSpring-5]
markers = [kFullCircle, kFullSquare, kOpenCircle, kOpenSquare, kOpenTriangleUp, kOpenTriangleDown, kOpenDiamond, kOpenCross, kOpenStar, kOpenStar, kOpenStar, kOpenStar, kOpenStar]
legend = ['occupancy integral', 'occupancy high','occupancy mid', 'occupancy low', 'occupancy integral GainEq',"pass3's correction"]

leg = TLegend(0.2, 0.3, 0.5, 0.5)
leg.SetFillStyle(0)
leg.SetBorderSize(0)
leg.SetTextSize(0.04)

# create TGraphs
gAbsDiff, gRelDiff = [], []
for i in range(len(inputFileNames)):
    if i != iRefFile:
        gAbsDiff.append(TGraphAsymmErrors(nPoints))
        gRelDiff.append(TGraphAsymmErrors(nPoints))
        SetObjectStyle(gAbsDiff[-1], color=colors[i], markerstyle=markers[i])
        SetObjectStyle(gRelDiff[-1], color=colors[i], markerstyle=markers[i])
        leg.AddEntry(gAbsDiff[-1],f'{legend[i]}', 'LP')

        ## fill TGraphs
        for iPoint in range(1, nPoints + 1):  # Bin index starts from 1 in ROOT
            xValue = histos[iRefFile].GetBinCenter(iPoint)
            xErrLow = histos[iRefFile].GetBinWidth(iPoint) / 2
            xErrHigh = histos[iRefFile].GetBinWidth(iPoint) / 2

            gAbsDiff[-1].SetPoint(iPoint - 1, xValue, absDiff[i][iPoint - 1])
            gAbsDiff[-1].SetPointError(iPoint - 1, xErrLow, xErrHigh, errAbsDiff[i][iPoint - 1], errAbsDiff[i][iPoint - 1])

            gRelDiff[-1].SetPoint(iPoint - 1, xValue, relDiff[i][iPoint - 1])
            gRelDiff[-1].SetPointError(iPoint - 1, xErrLow, xErrHigh, errRelDiff[i][iPoint - 1], errRelDiff[i][iPoint - 1])

# create canvas
## absolute difference
cAbsDiff = TCanvas('Abs_diff', 'Absolute difference', 800, 800)
cAbsDiff.DrawFrame(0, -0.05, 100, 0.05, ';#it{p}_{T} (GeV/#it{c}); Absolute difference')
#cAbsDiff.SetLogx()

Line = TLine()
Line.SetLineColor(kGray)
Line.SetLineStyle(2)
Line.SetLineWidth(4)

for i, g in enumerate(gAbsDiff):
    g.Draw('same pze')
leg.Draw()
Line.DrawLine(0, 0, 12, 0)
cAbsDiff.Draw()

## relative difference
cRelDiff = TCanvas('Rel_diff', 'Relative difference', 800, 800)
cRelDiff.DrawFrame(0, 0.98, 100, 1.02, ';#it{p}_{T} (GeV/#it{c}); Relative difference')
#cRelDiff.SetLogx()

# Line = TLine()
# Line.SetLineColor(kGray)
# Line.SetLineStyle(2)
# Line.SetLineWidth(4)

for i, g in enumerate(gRelDiff):
    g.Draw('same pze')
    # leg.AddEntry(g,f'{legend[i]}', 'LP')
leg.Draw()
Line.DrawLine(0, 1, 12, 1)
cRelDiff.Draw()
input('Press enter to exit')







cAbsDiff

# inputFileNames = '/home/wuct/localAnalysis/flow/DmesonAnalysis/comparisons/flow/fraction.root'

# inputFile = TFile(f'{inputFileNames}', 'r')

# set1 = inputFile.Get('g0')
# set2 = inputFile.Get('g1')
# set3 = inputFile.Get('g2')

# c = TCanvas('c', 'c', 800, 800)

# nPoints = set1.GetN()
# Dev2, Dev3 = [], []
# Ref2, Ref3 = [], []
# for i in range(nPoints):
#     Dev2.append(set2.GetY()[i] - set1.GetY()[i])
#     Dev3.append(set3.GetY()[i] - set1.GetY()[i])
#     print(f'Dev2: {Dev2[i]}, Dev3: {Dev3[i]}')
#     Ref2.append(set2.GetY()[i] / set1.GetY()[i])
#     Ref3.append(set3.GetY()[i] / set1.GetY()[i])

# # gDev2 = set1.Clone('gDev2')
# # gDev2.SetY
# # gDev3 = set1.Clone('gDev3')
# gDev2 = TGraphAsymmErrors(1)
# gDev3 = TGraphAsymmErrors(1)
# SetObjectStyle(gDev2, color=kRed, markerstyle=kOpenCircle)
# SetObjectStyle(gDev3, color=kRed, markerstyle=kOpenCircle)
# gRef2 = TGraphAsymmErrors(1)
# gRef3 = TGraphAsymmErrors(1)
# SetObjectStyle(gRef2, color=kRed, markerstyle=kOpenCircle)
# SetObjectStyle(gRef3, color=kRed, markerstyle=kOpenCircle)

# for i in range(nPoints):
#     gDev2.SetPoint(i, set1.GetX()[i], Dev2[i])
#     gDev2.SetPointError(i, set1.GetErrorXlow(i), set1.GetErrorXhigh(i), 0, 0)
#     gRef2.SetPoint(i, set1.GetX()[i], Ref2[i])
#     gRef2.SetPointError(i, set1.GetErrorXlow(i), set1.GetErrorXhigh(i), 0, 0)
#     # gDev2.SetPointError(iPt, (ptMax-ptMin)/2, (ptMax-ptMin)/2, vnResults['vnUnc'], vnResults['vnUnc'])
#     # gDev2.SetPointEYhigh(i, 0)
#     # gDev2.SetPointEYlow(i, 0)
#     # gDev2.SetMarkerColor(2)
#     # gDev2.SetMarkerStyle(20)
#     gDev3.SetPoint(i, set1.GetX()[i], Dev3[i])
#     print(f'gDev3: {Dev3[i]}')
#     gDev3.SetPointError(i, set1.GetErrorXlow(i), set1.GetErrorXhigh(i), 0, 0)
#     gRef3.SetPoint(i, set1.GetX()[i], Ref3[i])
#     gRef3.SetPointError(i, set1.GetErrorXlow(i), set1.GetErrorXhigh(i), 0, 0)
#     # gDev3.SetPointEYhigh(i, 0)
#     # gDev3.SetPointEYlow(i, 0)
#     # gDev3.SetMarkerColor(3)
#     # gDev3.SetMarkerStyle(20)

# # v2FileNames = [
# #         '/home/wuct/localAnalysis/flow/DmesonAnalysis/run3/flow/Results/2060/k3050/large/sp/ry/raw_yields3050l__set1_pol2.root', 
# #         '/home/wuct/localAnalysis/flow/DmesonAnalysis/run3/flow/Results/2060/k3050/large/sp/ry/raw_yields3050l__set2_pol2.root',
# #         '/home/wuct/localAnalysis/flow/DmesonAnalysis/run3/flow/Results/2060/k3050/large/sp/ry/raw_yields3050l__set3_pol2.root',
# # ]

# v2FileNames = [
#         '/home/wuct/localAnalysis/flow/stefano/DmesonAnalysis/run3/flow/PromptVn/promptvn_withsyst_3050_set1_pol2.root', 
#         '/home/wuct/localAnalysis/flow/stefano/DmesonAnalysis/run3/flow/PromptVn/promptvn_withsyst_3050_set2_pol2.root',
#         '/home/wuct/localAnalysis/flow/stefano/DmesonAnalysis/run3/flow/PromptVn/promptvn_withsyst_3050_set3_pol2.root',
# ]
# v2,vDev2,vDev3,vRef2,vRef3 = ([] for i in range(5))  # Define the variable v2 as an empty list
# gvnDev2 = TGraphAsymmErrors(1)
# gvnDev3 = TGraphAsymmErrors(1)
# SetObjectStyle(gvnDev2, color=kBlack, markerstyle=kFullCircle)
# SetObjectStyle(gvnDev3, color=kBlack, markerstyle=kFullCircle)
# gvnRef2 = TGraphAsymmErrors(1)
# gvnRef3 = TGraphAsymmErrors(1)
# SetObjectStyle(gvnRef2, color=kBlack, markerstyle=kFullCircle)
# SetObjectStyle(gvnRef3, color=kBlack, markerstyle=kFullCircle)

# for iFile, v2FileName in enumerate(v2FileNames):
#     v2File = TFile(f'{v2FileName}', 'r')
#     # v2.append(v2File.Get('hvnSimFit'))
#     v2.append(v2File.Get('gVnPromptStat'))
#     # v2[iFile].SetDirectory(0)

# # nPoints = v2[iFile].GetNbinsX()
# nPoints = v2[0].GetN()
# for i in range(nPoints):
#     # vDev2.append(v2[1].GetBinContent(i) - v2[0].GetBinContent(i))
#     # vDev3.append(v2[2].GetBinContent(i) - v2[0].GetBinContent(i))
#     # gvnDev2.SetPoint(i, v2[0].GetBinCenter(i), vDev2[i])
#     # gvnDev3.SetPoint(i, v2[0].GetBinCenter(i), vDev3[i])
#     vDev2.append(v2[1].GetY()[i] - v2[0].GetY()[i])
#     vDev3.append(v2[2].GetY()[i] - v2[0].GetY()[i])
#     gvnDev2.SetPoint(i, v2[0].GetX()[i], vDev2[i])
#     gvnDev2.SetPointError(i, v2[0].GetErrorXlow(i), v2[0].GetErrorXhigh(i), 0, 0)
#     gvnDev3.SetPoint(i, v2[0].GetX()[i], vDev3[i])
#     gvnDev3.SetPointError(i, v2[0].GetErrorXlow(i), v2[0].GetErrorXhigh(i), 0, 0)
#     vRef2.append(v2[1].GetY()[i] / v2[0].GetY()[i])
#     vRef3.append(v2[2].GetY()[i] / v2[0].GetY()[i])
#     gvnRef2.SetPoint(i, v2[0].GetX()[i], vRef2[i])
#     gvnRef2.SetPointError(i, v2[0].GetErrorXlow(i), v2[0].GetErrorXhigh(i), 0, 0)
#     gvnRef3.SetPoint(i, v2[0].GetX()[i], vRef3[i])
#     gvnRef3.SetPointError(i, v2[0].GetErrorXlow(i), v2[0].GetErrorXhigh(i), 0, 0)

#     # gvnDev2.SetMarkerColor(2)
#     # gvnDev2.SetMarkerStyle(20)
#     # gvnDev3.SetMarkerColor(2)
#     # gvnDev3.SetMarkerStyle(25)

# Latex = TLatex()
# Latex.SetNDC()
# Latex.SetTextSize(0.04)
# # Latex.SetTextFont(42)
# Line = TLine()
# Line.SetLineColor(kGray)
# Line.SetLineStyle(2)
# Line.SetLineWidth(4)
    
# leg = TLegend(0.2, 0.3, 0.5, 0.5)
# leg.SetFillStyle(0)
# leg.SetBorderSize(0)
# leg.SetTextSize(0.04)

# c = TCanvas('Absolute', '', 1600, 800)
# c.Divide(2,1)

# c.cd(1).DrawFrame(1, -0.1, 5, 0.1, ';#it{p}_{T} (GeV/#it{c}); Absolute value of difference')
# gDev3.Draw('same pez')
# leg.AddEntry(gDev3,f'Prompt fraction', 'LP')
# gvnDev3.Draw('same pez')
# leg.AddEntry(gvnDev3,f'v2', 'LP')
# leg.Draw()
# Latex.DrawLatex(0.4, 0.8, 'Set3 - Set1')
# Line.DrawLine(1, 0, 5, 0)


# c.cd(2).DrawFrame(1, -0.1, 5, 0.1, ';#it{p}_{T} (GeV/#it{c}); Absolute value of difference')
# gDev2.Draw('same pez')
# # leg.AddEntry(gDev2,f'fraction', 'LP')
# gvnDev2.Draw('same pez')
# # leg.AddEntry(gvnDev2,f'v2', 'LP')
# leg.Draw()
# Latex.DrawLatex(0.4, 0.8, 'Set2 - Set1')
# Line.DrawLine(1, 0, 5, 0)

# # leg.AddEntry(gResos[0],'vs. centrality', 'p')
# # gResos[0].Draw('p')
# # ResoMean = gResoMeans[0].GetPointY(0)
# # leg.AddEntry(gResoMeans[0],f'centrality integrated, #it{{R}}_{{2}} = {ResoMean:.5f}', 'LP')
# # gResoMeans[0].Draw('p')
# # leg.Draw()

# # c.cd(2).DrawFrame(0, 0, 5, 1.01, ';centrality (%); #it{R}_{2} {SP}')
# # gDev2.Draw('AP')
# # gDev3.Draw('P')
# # leg1.AddEntry(gResos[1],'vs. centrality', 'p')
# # gResos[1].Draw('p')
# # ResoMean = gResoMeans[1].GetPointY(0)
# # leg1.AddEntry(gResoMeans[1],f'centrality integrated, #it{{R}}_{{2}} = {ResoMean:.5f}', 'LP')
# # gResoMeans[1].Draw('p')
# # leg1.Draw()
# c.Draw()
# c.SaveAs('CompTemp.root')

# leg1 = TLegend(0.2, 0.3, 0.5, 0.5)
# leg1.SetFillStyle(0)
# leg1.SetBorderSize(0)
# leg1.SetTextSize(0.04)

# c1 = TCanvas('Relative', '', 1600, 800)
# c1.Divide(2,1)

# c1.cd(1).DrawFrame(1, 0.5, 5, 1.5, ';#it{p}_{T} (GeV/#it{c}); Relative difference')
# gRef3.Draw('same pez')
# leg1.AddEntry(gRef3,f'Prompt fraction', 'LP')
# gvnRef3.Draw('same pez')
# leg1.AddEntry(gvnRef3,f'v2', 'LP')
# leg.Draw()
# Latex.DrawLatex(0.4, 0.8, 'Set3 / Set1')
# Line.DrawLine(1, 1, 5, 1)

# c1.cd(2).DrawFrame(1, 0.5, 5, 1.5, ';#it{p}_{T} (GeV/#it{c}); Relative difference')
# gRef2.Draw('same pez')
# # leg.AddEntry(gDev2,f'fraction', 'LP')
# gvnRef2.Draw('same pez')
# # leg.AddEntry(gvnDev2,f'v2', 'LP')
# leg1.Draw()
# Latex.DrawLatex(0.4, 0.8, 'Set2 / Set1')
# Line.DrawLine(1, 1, 5, 1)

# c1.Draw()
# #c1.SaveAs('CompTemp.root')

# # gDev2.Draw('AP')
# # gDev3.Draw('P')
# input('Press enter to exit')

# # def compare(configName):
        
# #         with open(configName, 'r') as ymlCfgFile:
# #             config = yaml.load(ymlCfgFile, yaml.FullLoader)
# #         inputFileNames = config[inputFileNames]
# #         histNames = config[histNames]

# #         plots = []
# #         for iFile, inputFileName in enumerate(inputFileNames):
# #             inputfile = TFile(f'{inputFileName}')
# #             histName = histNames[iFile]
# #             if str(type(inputfile.Get(histNames[iFile]))).split('.')[-1].split(' ')[0] != 'TGraphAsymmErrors':
# #                 plots.append(inputfile.Get(histName))
# #                 plots[iFile].SetDirectory(0)
# #             else:
# #                 plots.append(inputfile.Get(histName))

            

# # if __name__ == "__main__":

# #     parser = argparse.ArgumentParser(description='Arguments')
# #     parser.add_argument('cfgFileName', metavar='text', default='config_Template.yml')
# #     args = parser.parse_args()

# #     compare(
# #         args.cfgFileName
# #     )

# # input('Press enter to exit')