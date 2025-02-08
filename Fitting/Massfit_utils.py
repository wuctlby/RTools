# Import necessary libraries
# import numpy as np
import matplotlib.pyplot as plt
# import uproot
# import hist
# from flarefly.data_handler import DataHandler
# from flarefly.fitter import F2MassFitter
# import ROOT
# from PyPDF2 import PdfWriter
import os
import sys
import ROOT
import yaml
import numpy as np
import argparse
sys.path.append('..')
from utils.Load import load_histos, load_non_dir_objects
from flarefly.data_handler import DataHandler
from flarefly.fitter import F2MassFitter
from PyPDF2 import PdfWriter

def Mass_fit_ff(inputFile, histoName, MassMin, MassMax, Rebin, SgnFunc, BkgFunc, FixSigma=False, FixSigmaFromFile='', iPt=0):
    
    dataMassRebined = DataHandler(data=inputFile, histoname=histoName, 
                        limits=[MassMin, MassMax], rebin=Rebin)

    # Check if data is binned
    if not dataMassRebined.get_is_binned():
        return

    if not isinstance(SgnFunc, list):
        SgnFunc = [SgnFunc]
    if not isinstance(BkgFunc, list):
        BkgFunc = [BkgFunc]
    
    fitter = F2MassFitter(data_handler=dataMassRebined,
                          name_signal_pdf=SgnFunc,
                          name_background_pdf=BkgFunc,
                          name=f"{BkgFunc}_{SgnFunc}")
    if FixSigma:
        if FixSigmaFromFile != '':
            file = ROOT.TFile.Open(FixSigmaFromFile)
            FixedSigma = file.Get("hRawYieldsSigma").GetBinContent(iPt+1)
            fitter.set_signal_initpar(0, "sigma", FixedSigma, fix=True)
    else:
        fitter.set_signal_initpar(0, "sigma", 0.016, limits=[0.005, 0.05])

    # Initiate fit parameters
    fitter.set_particle_mass(0, pdg_id=421, limits=[1.850, 1.890])
    fitter.set_signal_initpar(0, "frac", 0.0001)
    fitter.set_background_initpar(0, "c0", 2)
    fitter.set_background_initpar(0, "c1", -0.1)
    fitter.set_background_initpar(0, "c2", -0.01)

    # Fit
    fitter.mass_zfit()
    
    return fitter

def collect_fit_results(fitter, iPt):
    mean, meanError = fitter.get_mass()
    sigma, sigmaError = fitter.get_sigma()
    rawyield, rawyieldError = fitter.get_raw_yield(0)
    significance, signifError = fitter.get_significance()
    bkg, bkgError = fitter.get_background()
    chi2ndf = fitter.get_chi2_ndf()
    soverb, soverbError = fitter.get_signal_over_background()
    
    # Estimate correlation coefficient
    rho = rawyieldError / bkgError
    if rho > 1.:
        rho = 1. / rho

    # Calculate purity and its uncertainty
    purity = rawyield / (rawyield + bkg)
    purityError = np.sqrt(
        (rawyieldError**2 / (rawyield + bkg)**2) +
        (rawyield**2 * bkgError**2 / (rawyield + bkg)**4) -
        (2 * rho * rawyield * rawyieldError * bkgError / (rawyield + bkg)**3)
    )

    return {
        'mean': mean,
        'meanError': meanError,
        'sigma': sigma,
        'sigmaError': sigmaError,
        'rawyield': rawyield,
        'rawyieldError': rawyieldError,
        'significance': significance,
        'signifError': signifError,
        'bkg': bkg,
        'bkgError': bkgError,
        'chi2ndf': chi2ndf,
        'soverb': soverb,
        'soverbError': soverbError,
        'purity': purity,
        'purityError': purityError
    }
    
def define_plot_texts(results, ptmin, ptmax, cent):
    latex_expr_mass = f"$\mu=$" + str(round(results['mean'], 4)) + f"$\pm$" + str(round(results['meanError'], 4)) + "$\;\mathrm{GeV}/c^2$"
    latex_expr_width = f"$\sigma=$" + str(round(results['sigma'], 3)) + f"$\pm$" + str(round(results['sigmaError'], 3)) + "$\;\mathrm{GeV}/c^2$"
    latex_expr_rawyield = r"$N_{\mathrm{D}^{\mathrm{0}}}\:=\:$" + str(int(results['rawyield'])) + f"$\:\pm\:$" + str(int(results['rawyieldError']))
    latex_expr_significance = r"$s/\sqrt{s+b}\:(3\sigma)\:=\:$" + str(round(results['significance'], 1)) + f"$\:\pm\:$" + str(round(results['signifError'], 1))
    latex_expr_purity = f"Purity (s/(s+b))$\:=\:$"+str(round(results['purity'],3))+f"$\:\pm\:$"+str(round(results['purityError'],3))

    return {
        'latex_expr_mass': latex_expr_mass,
        'latex_expr_width': latex_expr_width,
        'latex_expr_rawyield': latex_expr_rawyield,
        'latex_expr_significance': latex_expr_significance,
        'latex_expr_purity': latex_expr_purity,
        'pt_range': f'{ptmin} < $p_{{\mathrm{{T}}}} < {ptmax} \: \mathrm{{GeV/c}}$',
        'cent_text': rf'{cent}$\% ~\mathrm{{Pb-Pb}}, \sqrt{{\it{{s}}_\mathrm{{NN}}}} = 5.36 \: \mathrm{{TeV}}$'
    }
    
def save_plots(fitter, texts, outputDir, ptmin, ptmax, iFile, suffix):
    # Plot the mass fit
    plotMassFit, axse = fitter.plot_mass_fit(style="ATLAS", show_extra_info=False, extra_info_loc=['upper left', 'lower right'], axis_title=r"$M_{K\pi} (\mathrm{GeV}/c^2)$")
    plotMassFit.text(0.195, 0.83, r'$\mathrm{D^0} \rightarrow \mathrm{K}^- \mathrm{\pi}^+ + \mathrm{c.c.}$')
    plotMassFit.text(0.195, 0.79, texts['cent_text'])
    plotMassFit.text(0.195, 0.75, texts['pt_range'])
    plotMassFit.text(0.62, 0.67, texts['latex_expr_mass'], fontsize=13)
    plotMassFit.text(0.62, 0.62, texts['latex_expr_width'], fontsize=13)
    plotMassFit.text(0.195, 0.40, texts['latex_expr_rawyield'], fontsize=15)
    plotMassFit.text(0.195, 0.35, texts['latex_expr_significance'], fontsize=15)
    plotMassFit.text(0.195, 0.30, texts['latex_expr_purity'], fontsize=15)

    # Save the plot for each pT bin
    plotMassFitName = f'{outputDir}/rawyield/temp_fitSpectrum_pT_{ptmin}_{ptmax}_file_{iFile}_{suffix}.pdf'
    plotMassFit.savefig(plotMassFitName)
    plt.close(plotMassFit)

    # Save residuals
    plotRawResiduals = fitter.plot_raw_residuals(style="ATLAS", axis_title=r"$M_{pK\pi}$")
    plotRawResiduals.text(0.195, 0.75, texts['pt_range'])
    plotRawResidualsName = f'{outputDir}/rawyield/temp_fitResiduals_pT_{ptmin}_{ptmax}_file_{iFile}_{suffix}.pdf'
    plotRawResiduals.savefig(plotRawResidualsName)
    plt.close(plotRawResiduals)

    return plotMassFitName, plotRawResidualsName

def main(config_fit, inputFiles, outputDir, cent, suffix):
    # Load configuration file
    with open(config_fit, 'r') as cfgFit:
        config = yaml.safe_load(cfgFit)

    # pt bins
    if 'ptBins' in config:
        ptBins = config['ptBins']
    else:
        ptmins = config['ptmins']
        ptmaxs = config['ptmaxs']
        ptBins = list(set(ptmins + ptmaxs))
        ptBins.sort()
    nPtBins = len(ptBins) - 1
    inputFiles = config['inputFiles'] if 'inputFiles' in config and config['inputFiles'] else inputFiles
    FixSigma = config['FixSigma'] if 'FixSigma' in config else False
    FixSigmaFromFile = config['FixSigmaFromFile'] if 'FixSigmaFromFile' in config else ''
    SgnFuncs = config['SgnFunc']
    BkgFuncs = config['BkgFunc']
    MassMins = config['MassMin']
    MassMaxs = config['MassMax']
    Rebins= config['Rebin']
    
    os.makedirs(f"{outputDir}/rawyield", exist_ok=True)
    
    if len(MassMins) < nPtBins or len(MassMaxs) < nPtBins:
        print(f"Number of mass ranges({len(MassMins)}, {len(MassMaxs)}) is less to the number of pT bins ({nPtBins}).")
        sys.exit()
    
    residualPDFs, rawYieldPDFs, allPDFs = [], [], []
    hMasses, hSigmas, hRawYields, hBkgs, hSignificances, hChi2s, hSoverBs = [], [], [], [], [], [], []
    # hPuritys = []
    hMass = ROOT.TH1F(f"hRawYieldsMean", f"Mass vs pT; pT (GeV/c); Mass (GeV/c^2)", nPtBins, np.array(ptBins, dtype="float64"))
    hSigma = ROOT.TH1F(f"hRawYieldsSigma", f"Sigma vs pT; pT (GeV/c); Sigma (GeV/c^2)", nPtBins, np.array(ptBins, dtype="float64"))
    hRawYield = ROOT.TH1F(f"hRawYields", f"Raw Yield vs pT; pT (GeV/c); Raw Yield", nPtBins, np.array(ptBins, dtype="float64"))
    hBkg = ROOT.TH1F(f"hRawYieldsBkg", f"Background vs pT; pT (GeV/c); Background", nPtBins, np.array(ptBins, dtype="float64"))
    hSignificance = ROOT.TH1F(f"hRawYieldsSignificance", f"Significance vs pT; pT (GeV/c); Significance", nPtBins, np.array(ptBins, dtype="float64"))
    hChi2 = ROOT.TH1F(f"hRawYieldsChiSquare", f"Chi2 vs pT; pT (GeV/c); Bkg", nPtBins, np.array(ptBins, dtype="float64"))
    hSoverB = ROOT.TH1F(f"hRawYieldsSoverB", f"Signal over Background vs pT; pT (GeV/c); S / B", nPtBins, np.array(ptBins, dtype="float64"))
    # hPurity = ROOT.TH1F("hRawYieldsPurity", "Purity vs kstar; k* (GeV/c); Purity", n_bins, np.array(pt_bins, dtype="float64"))
    
    for iFile, inputFile in enumerate(inputFiles):
        histoNames = load_histos(inputFile, "hist_mass", keyWord=True, onlyPath=True)
        if len(histoNames) != nPtBins:
            print(f"Number of histograms {len(histoNames)} in the input file {inputFile} is not equal to the number of pT bins({nPtBins}).")
            sys.exit()
            
        for iPt, (ptmin, ptmax, histoName, MassMin, MassMax, Rebin, SgnFunc, BkgFunc) in enumerate(zip(ptmins, ptmaxs, histoNames, MassMins, MassMaxs, Rebins, SgnFuncs, BkgFuncs)):
            fitter = Mass_fit_ff(inputFile, histoName, MassMin, MassMax, Rebin, SgnFunc, BkgFunc, FixSigma, FixSigmaFromFile, iPt)
            results = collect_fit_results(fitter, iPt)
            texts = define_plot_texts(results, ptmin, ptmax, cent)
            plotMassFitName, plotRawResidualsName = save_plots(fitter, texts, outputDir, ptmin, ptmax, iFile, suffix)
            
            rawYieldPDFs.append(plotMassFitName)
            residualPDFs.append(plotRawResidualsName)
            allPDFs.extend([plotMassFitName, plotRawResidualsName])

            # Fill ROOT histograms with fit results and errors
            iBin = iPt + 1  # ROOT bin index starts from 1
            hMass.SetBinContent(iBin, results['mean'])
            hMass.SetBinError(iBin, results['meanError'])
            hSigma.SetBinContent(iBin, results['sigma'])
            hSigma.SetBinError(iBin, results['sigmaError'])
            hRawYield.SetBinContent(iBin, results['rawyield'])
            hRawYield.SetBinError(iBin, results['rawyieldError'])
            hBkg.SetBinContent(iBin, results['bkg'])
            hBkg.SetBinError(iBin, results['bkgError'])
            hSignificance.SetBinContent(iBin, results['significance'])
            hSignificance.SetBinError(iBin, results['signifError'])
            hChi2.SetBinContent(iBin, results['chi2ndf'])
            hSoverB.SetBinContent(iBin, results['soverb'])
            hSoverB.SetBinError(iBin, results['soverbError'])
            # hPurity.SetBinContent(iBin, results['purity'])
            # hPurity.SetBinError(iBin, results['purityError'])

        # Write fit results histograms to a separate ROOT file for each file_index
        output = ROOT.TFile(f"{outputDir}/rawyield/RawYields_D0_PbPb_{iFile}_{suffix}.root", "RECREATE")
        hMass.Write()
        hSigma.Write()
        hRawYield.Write()
        hBkg.Write()
        hSignificance.Write()
        hChi2.Write()
        hSoverB.Write()
        # hPurity.Write()
        output.Close()

        # Clear the histograms after writing to avoid conflicts
        hMass.Reset()
        hSigma.Reset()
        hRawYield.Reset()
        hSignificance.Reset()
        hBkg.Reset()
        hChi2.Reset()
        hSoverB.Reset()
        # hPurity.Reset()

    # Create a single PDF file from the generated PDFs
    pdfFiles = rawYieldPDFs + residualPDFs
    rawyieldPdf = f'{outputDir}/rawyield/fitSpectrum_D0_PbPb_{suffix}.pdf'
    residualPdf = f'{outputDir}/rawyield/fitResiduals_D0_PbPb_{suffix}.pdf'
    combinedPdf = f'{outputDir}/rawyield/RawYields_D0_PbPb_{suffix}.pdf'

    with PdfWriter() as pdfWriter:
        for pdfFile in pdfFiles:
            pdfWriter.append(pdfFile)
        pdfWriter.write(combinedPdf)

    with PdfWriter() as pdfWriter:
        for pdfFile in rawYieldPDFs:
            pdfWriter.append(pdfFile)
        pdfWriter.write(rawyieldPdf)

    with PdfWriter() as pdfWriter:
        for pdfFile in residualPDFs:
            pdfWriter.append(pdfFile)
        pdfWriter.write(residualPdf)
        
    os.system(f"rm {' '.join(allPDFs)}")

    print(f"Fit results with errors saved to RawYields_D0_PbPb_{suffix}.root")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("config_fit", metavar='text', 
                        default="config_fit.yaml", help="Configuration file for the fit")
    parser.add_argument("--inputFiles", "-i", metavar='list', nargs='+', 
                        default="AnalysisResults.root", help="Input files")
    parser.add_argument("--outputDir", "-o", metavar='text',
                        default=".", help="Output directory")
    parser.add_argument("--cent", "-c", metavar='text',
                        default="k3050", help="Centrality")
    parser.add_argument("--suffix", "-s", metavar='text',
                        default="All", help="Suffix for the output files")
    args = parser.parse_args()

    main(
        config_fit=args.config_fit,
        inputFiles=args.inputFiles,
        outputDir=args.outputDir,
        cent=args.cent,
        suffix=args.suffix
    )