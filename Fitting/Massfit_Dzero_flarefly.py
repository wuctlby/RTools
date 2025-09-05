# Import necessary libraries
# import numpy as np
# import matplotlib.pyplot as plt
# import uproot
# import hist
# from flarefly.data_handler import DataHandler
# from flarefly.fitter import F2MassFitter
# import ROOT
# from PyPDF2 import PdfWriter
# Author: Z. Biao biao.zhang@cern.ch
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
        fitter.set_signal_initpar(0, "sigma", 0.016, limits=[0.005, 0.07])

    # Initiate fit parameters
    fitter.set_particle_mass(0, pdg_id=421, limits=[1.850, 1.890])
    fitter.set_signal_initpar(0, "frac", 0.0001)
    fitter.set_background_initpar(0, "c0", 2)
    fitter.set_background_initpar(0, "c1", -0.1)
    fitter.set_background_initpar(0, "c2", -0.01)

    # Fit
    fitter.mass_zfit()
    
    return fitter

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
    outputDir = config['outputDir'] if 'outputDir' in config and config['outputDir'] else outputDir
    cent = config['cent'] if 'cent' in config and config['cent'] else cent
    suffix = config['suffix'] if 'suffix' in config and config['suffix'] else suffix
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
        # histoNames = load_histos(inputFile, "fM/fM", keyWord=True, onlyPath=True)
        # if len(histoNames) != nPtBins:
        #     print(f"Number of histograms {len(histoNames)} in the input file {inputFile} is not equal to the number of pT bins({nPtBins}).")
        #     sys.exit()
        
        if iFile != 0:
            continue
        
        # histoNames = []
        # histos = []
        # for i, infile in enumerate(inputFiles):
        #     file = ROOT.TFile.Open(infile)
        #     obj = file.GetListOfKeys()
        #     for key in obj:
        #         print(key.GetName())
        #         print(key.GetClassName())
        #     tree = file.Get("fM")
        #     hname = "h_fM"
        #     ROOT.gDirectory.Delete(hname + ";*") 
        #     tree.Draw(f"fM>>{hname}", "fM > 1.65 && fM < 2.15", "e1")
        #     histo = ROOT.gDirectory.Get(hname)
        #     histo.SetDirectory(0)
        #     histo.SetName(f"h_fM_{i}")
        #     histos.append(histo)
        #     histoNames.append(histo.GetName())
        #     file.Close()
        # massfile = ROOT.TFile.Open(outputDir + "mass.root", "RECREATE")
        # for histo in histos:
        #     histo.Write()
        # massfile.Close()
        # inputFile = outputDir + "mass.root"
        histoNames= []
        for file in inputFiles:
            infile = ROOT.TFile.Open(file)
            histo = infile.Get("hist_inv_mass_origin_ptSmear1.5+phi_FD")
            
            histoNames.append(histo.GetName())
        
        for iPt, (ptmin, ptmax, histoName, MassMin, MassMax, Rebin, SgnFunc, BkgFunc) \
                in enumerate(zip(ptmins, ptmaxs, histoNames, MassMins, MassMaxs, Rebins, SgnFuncs, BkgFuncs)):
  
            fitter, rovers = Mass_fit_ff(inputFiles[iPt], histoName, MassMin, MassMax, Rebin, SgnFunc, BkgFunc, FixSigma, FixSigmaFromFile, iPt)

            # Get fit results with errors
            mean, meanError = fitter.get_mass()
            sigma, sigmaError = fitter.get_sigma()
            rawyield, rawyieldError = fitter.get_raw_yield(0)
            significance, signifError = fitter.get_significance()
            bkg, bkgError = fitter.get_background()
            chi2ndf = fitter.get_chi2_ndf()
            # soverb, soverbError = fitter.get_signal_over_background()
            # purity = rawyield / (rawyield + bkg)
            n, nError = fitter.get_signal_parameter(0, "n")
            alpha, alphaError = fitter.get_signal_parameter(0, "alpha")
            
            # # Estimate correlation coefficient
            # rho = rawyieldError / bkgError
            # if rho > 1.:
            #     rho = 1. / rho
        
            # # Calculate purity and its uncertainty
            # purity = rawyield / (rawyield + bkg)
            # purityError = np.sqrt(
            # (rawyieldError**2 / (rawyield + bkg)**2) +
            # (rawyield**2 * bkgError**2 / (rawyield + bkg)**4) -
            # (2 * rho * rawyield * rawyieldError * bkgError / (rawyield + bkg)**3)
            # )

            latex_expr_mass = f"$\mu=$" + str(round(mean, 4)) + f"$\pm$" + str(round(meanError, 4)) + "$\;\mathrm{GeV}/c^2$"
            latex_expr_width = f"$\sigma=$" + str(round(sigma, 3)) + f"$\pm$" + str(round(sigmaError, 3)) + "$\;\mathrm{GeV}/c^2$"
            latex_expr_rawyield = r"$N_{\mathrm{D}^{\mathrm{0}}}\:=\:$" + str(int(rawyield)) + f"$\:\pm\:$" + str(int(rawyieldError))
            latex_expr_rovers = r"$r/s\:=\:$" + str(round(rovers, 3))
            latex_expr_significance = r"$s/\sqrt{s+b}\:(3\sigma)\:=\:$" + str(round(significance, 1)) + f"$\:\pm\:$" + str(round(signifError, 1))
            # latex_expr_purity = f"Purity (s/(s+b))$\:=\:$"+str(round(purity,3))+f"$\:\pm\:$"+str(round(purityError,3))

            # Plot the mass fit
            plotMassFit, axse = fitter.plot_mass_fit(style="ATLAS", show_extra_info=False, extra_info_loc=['upper left', 'lower right'], axis_title=r"$M_{K\pi} (\mathrm{GeV}/c^2)$")
            plotMassFit.text(0.195, 0.83, r'$\mathrm{D^0} \rightarrow \mathrm{K}^- \mathrm{\pi}^+ + \mathrm{c.c.}$')
            plotMassFit.text(0.195, 0.79, rf'{cent}$\% ~\mathrm{{Pb-Pb}}, \sqrt{{\it{{s}}_\mathrm{{NN}}}} = 5.36 \: \mathrm{{TeV}}$')
            plotMassFit.text(0.195, 0.75, f'{ptmin} < $p_{{\mathrm{{T}}}} < {ptmax} \: \mathrm{{GeV/c}}$')
            plotMassFit.text(0.62, 0.67, latex_expr_mass, fontsize=13)
            plotMassFit.text(0.62, 0.62, latex_expr_width, fontsize=13)
            plotMassFit.text(0.195, 0.40, latex_expr_rawyield, fontsize=15)
            plotMassFit.text(0.195, 0.35, latex_expr_rovers, fontsize=15)
            # plotMassFit.text(0.195, 0.35, latex_expr_significance, fontsize=15)
            # plotMassFit.text(0.195, 0.30, latex_expr_purity, fontsize=15)

            # Save the plot for each pT bin
            plotMassFitName = f'{outputDir}/rawyield/temp_fitSpectrum_pT_{ptmin}_{ptmax}_file_{iFile}_{suffix}.pdf'
            plotMassFit.savefig(plotMassFitName)
            rawYieldPDFs.append(plotMassFitName)
            allPDFs.append(plotMassFitName)

            # Save residuals
            plotRawResiduals = fitter.plot_raw_residuals(style="ATLAS", axis_title=r"$M_{pK\pi}$")
            plotRawResiduals.text(0.195, 0.75, f'{ptmin} < $p_{{\mathrm{{T}}}} < {ptmax} \: \mathrm{{GeV/c}}$')
            plotRawResidualsName = f'{outputDir}/rawyield/temp_fitResiduals_pT_{ptmin}_{ptmax}_file_{iFile}_{suffix}.pdf'
            plotRawResiduals.savefig(plotRawResidualsName)
            residualPDFs.append(plotRawResidualsName)
            allPDFs.append(plotRawResidualsName)

            # Fill ROOT histograms with fit results and errors
            iBin = iPt + 1  # ROOT bin index starts from 1

            hMass.SetBinContent(iBin, mean)
            hMass.SetBinError(iBin, meanError)

            hSigma.SetBinContent(iBin, sigma)
            hSigma.SetBinError(iBin, sigmaError)

            hRawYield.SetBinContent(iBin, rawyield)
            hRawYield.SetBinError(iBin, rawyieldError)

            hBkg.SetBinContent(iBin, bkg)
            hBkg.SetBinError(iBin, bkgError)

            # hSignificance.SetBinContent(iBin, significance)
            # hSignificance.SetBinError(iBin, signifError)
            
            hChi2.SetBinContent(iBin, chi2ndf)
            # hSoverB.SetBinContent(iBin, soverb)
            # hSoverB.SetBinError(iBin, soverbError)
            
            hRoverS.SetBinContent(iBin, rovers)
            hRoverS.SetBinError(iBin, 0.0)
            
            halpha.SetBinContent(iBin, alpha)
            halpha.SetBinError(iBin, alphaError)
            hN.SetBinContent(iBin, n)
            hN.SetBinError(iBin, nError)
            
            # hPurity.SetBinContent(iBin, purity)
            # hPurity.SetBinError(iBin, purityError)

        # %% Write fit results histograms to a separate ROOT file for each file_index
        output = ROOT.TFile(f"{outputDir}/rawyield/RawYields_D0_PbPb_{iFile}_{suffix}.root", "RECREATE")
        hMass.Write()
        hSigma.Write()
        hRawYield.Write()
        hBkg.Write()
        hSignificance.Write()
        hChi2.Write()
        hSoverB.Write()
        hRoverS.Write()
        halpha.Write()
        hN.Write()
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
        hRoverS.Reset()
        halpha.Reset()
        hN.Reset()
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