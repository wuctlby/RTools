import pyarrow.parquet as pq
import uproot3 as uproot
import numpy as np
import ROOT
from ROOT import TH1F
import sys
sys.path.append('../../')
from ROOT import TFile, TCanvas, TLegend, TLatex
from ROOT import TFile, TH1F, TH2F, TCanvas, TLegend, TGraphAsymmErrors, TLatex, gRandom, TF1  # pylint: disable=import-error,no-name-in-module
from ROOT import kBlack, kRed, kAzure, kGreen, kRainBow # pylint: disable=import-error,no-name-in-module
from ROOT import kFullCircle, kFullSquare, kOpenSquare, kOpenCircle, kOpenCross, kOpenDiamond # pylint: disable=import-error,no-name-in-module

from utils.StyleFormatter import SetGlobalStyle, SetObjectStyle
from utils.AnalysisUtils import GetPromptFDYieldsAnalyticMinimisation, ApplyVariationToList

def compute_efficiency(sig_cut, bkg_cut, PromptTree, FDTree):

    totel_prompt = PromptTree.Count().GetValue()
    totel_FD = FDTree.Count().GetValue()
    hEffPromptVsCut = TH1F(f'hEffPromptVsCut', f';efficiency', len(sig_cuts), 0.5, len(sig_cuts) + 0.5)
    hEffFDVsCut = TH1F(f'hEffFDVsCut', f';efficiency', len(sig_cuts), 0.5, len(sig_cuts) + 0.5)

    SetObjectStyle(hEffPromptVsCut, color=kRed+1, markerstyle=kFullCircle)
    SetObjectStyle(hEffFDVsCut, color=kAzure+4, markerstyle=kFullSquare)

    legEff = TLegend(0.2, 0.2, 0.4, 0.4)
    legEff.SetFillStyle(0)
    legEff.SetBorderSize(0)
    legEff.SetTextSize(0.045)

    legEff.AddEntry(hEffPromptVsCut, 'Prompt', 'lpe')
    legEff.AddEntry(hEffFDVsCut, 'Non-prompt', 'lpe')
    for icut, (sig_cut, bkg_cut) in enumerate(zip(sig_cuts, bkg_cuts)):
        sel_prompt = PromptTree.Filter(f"ML_output_Bkg < {bkg_cut} && ML_output_NonPrompt > {sig_cut}")
        sel_FD = FDTree.Filter(f"ML_output_Bkg < {bkg_cut} && ML_output_NonPrompt > {sig_cut}")
        n_prompt = sel_prompt.Count().GetValue()
        n_FD = sel_FD.Count().GetValue()
        eff_prompt = n_prompt / totel_prompt
        eff_FD = n_FD / totel_FD
        print(f"sig_cut: {sig_cut}, bkg_cut: {bkg_cut}, prompt: {eff_prompt}, FD: {eff_FD}")

        hEffPromptVsCut.SetBinContent(icut + 1, eff_prompt)
        hEffPromptVsCut.SetBinError(icut + 1, eff_prompt*0.01)
        hEffFDVsCut.SetBinContent(icut + 1, eff_FD)
        hEffFDVsCut.SetBinError(icut + 1, eff_FD*0.01)

    cEff = TCanvas(f'cEff', '', 800, 800)
    cEff.DrawFrame(0.5, hEffPromptVsCut.GetMinimum()/5, len(sig_cuts) + 0.5, 1., f';cutset;efficiency')
    cEff.SetLogy()
    hEffPromptVsCut.DrawCopy('same lp')
    hEffFDVsCut.DrawCopy('same lp')
    legEff.Draw()

    cEff.Draw()
    cEff.SaveAs('efficiency.png')
    input("Press Enter to exit.")



if __name__ == "__main__":

    # 读取 Parquet 文件
    parquet_file = [
        '/home/wuct/ALICE/local/DmesonAnalysis/RTools/ML/results/Training_303753/pt2_3/Prompt_pT_2_3_ModelApplied.parquet.gzip',
        '/home/wuct/ALICE/local/DmesonAnalysis/RTools/ML/results/Training_303753/pt2_3/FD_pT_2_3_ModelApplied.parquet.gzip',
        '/home/wuct/ALICE/local/DmesonAnalysis/RTools/ML/results/Training_303753/pt2_3/Data_pT_2_3_ModelApplied.parquet.gzip'
    ]
    # parquet_file = '/home/wuct/ALICE/local/DmesonAnalysis/RTools/ML/results/Training_med/pt2_3/Prompt_pT_2_3_ModelApplied.parquet.gzip'
    out_file = [
        '/home/wuct/ALICE/local/DmesonAnalysis/RTools/ML/results/Training_303753/pt2_3/Prompt_pT_2_3_ModelApplied.root',
        '/home/wuct/ALICE/local/DmesonAnalysis/RTools/ML/results/Training_303753/pt2_3/FD_pT_2_3_ModelApplied.root',
        '/home/wuct/ALICE/local/DmesonAnalysis/RTools/ML/results/Training_303753/pt2_3/Data_pT_2_3_ModelApplied.root'
    ]

    sig_cuts = list(np.arange(0.2, 0.8, 0.02))
    print(sig_cuts)
    bkg_cuts = [0.001 for _ in sig_cuts]
    prompt_file = ROOT.TFile(out_file[0], "read")
    FD_file = ROOT.TFile(out_file[1], "read")

    prompt_tree = prompt_file.Get("tree")
    FD_tree = FD_file.Get("tree")

    PromptTree = ROOT.RDataFrame(prompt_tree)
    FDTree = ROOT.RDataFrame(FD_tree)

    compute_efficiency(sig_cuts, bkg_cuts, PromptTree, FDTree)
