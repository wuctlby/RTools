'''
python script for the McMatchCheck using TTrees or pandas dataframes as input
run: python McMatchCheck.py cfgFileName.yml
'''

import sys
import argparse
import time
import numpy as np
import uproot
import pandas as pd
import yaml
from alive_progress import alive_bar
from ROOT import TFile, TTree, TH1F, TH2F, TF1, TCanvas, TNtuple, TLegend  # pylint: disable=import-error,no-name-in-module
from ROOT import gROOT, kRainBow  # pylint: disable=import-error,no-name-in-module
from ROOT import kRed, kAzure, kFullCircle, kOpenSquare  # pylint: disable=import-error,no-name-in-module
sys.path.insert(0, '..')
from utils.AnalysisUtils import ComputeEfficiency, GetPromptFDFractionFc, GetExpectedBkgFromSideBands  #pylint: disable=wrong-import-position,import-error
from utils.StyleFormatter import SetGlobalStyle, SetObjectStyle  #pylint: disable=wrong-import-position,import-error
from utils.DfUtils import LoadDfFromRootOrParquet  #pylint: disable=wrong-import-position,import-error
from utils.ReadModel import ReadTAMU, ReadPHSD, ReadMCatsHQ, ReadCatania  #pylint: disable=wrong-import-position,import-error
from utils.FitUtils import SingleGaus

parser = argparse.ArgumentParser(description='Arguments to pass')
parser.add_argument('cfgFileName', metavar='text', default='cfgFileName.yml',
					help='config file name with root input files')
parser.add_argument("--batch", help="suppress video output",
					action="store_true")
args = parser.parse_args()

with open(args.cfgFileName, 'r') as ymlCfgFile:
	inputCfg = yaml.load(ymlCfgFile, yaml.FullLoader)
# load dataframes from input files
dfPrompt = LoadDfFromRootOrParquet(inputCfg['infiles']['signal']['prompt']['filename'],
								   inputCfg['infiles']['signal']['prompt']['dirname'],
								   inputCfg['infiles']['signal']['prompt']['treename'])
dfFD = LoadDfFromRootOrParquet(inputCfg['infiles']['signal']['feeddown']['filename'],
							   inputCfg['infiles']['signal']['feeddown']['dirname'],
							   inputCfg['infiles']['signal']['feeddown']['treename'])
dfBkg_tot = LoadDfFromRootOrParquet(inputCfg['infiles']['background']['filename'],
									inputCfg['infiles']['background']['dirname'],
									inputCfg['infiles']['background']['treename'])
if inputCfg['infiles']['secpeak']['prompt']['filename']:
	dfSecPeakPrompt = LoadDfFromRootOrParquet(inputCfg['infiles']['secpeak']['prompt']['filename'],
											  inputCfg['infiles']['secpeak']['prompt']['dirname'],
											  inputCfg['infiles']['secpeak']['prompt']['treename'])
else:
	dfSecPeakPrompt = None
if inputCfg['infiles']['secpeak']['feeddown']['filename']:
	dfSecPeakFD = LoadDfFromRootOrParquet(inputCfg['infiles']['secpeak']['feeddown']['filename'],
										  inputCfg['infiles']['secpeak']['feeddown']['dirname'],
										  inputCfg['infiles']['secpeak']['feeddown']['treename'])
else:
	dfSecPeakFD = None

# load cut values to scan
ptMins = inputCfg['ptmin']
ptMaxs = inputCfg['ptmax']
ptLims = list(ptMins)
ptLims.append(ptMaxs[-1])
if not isinstance(ptMins, list):
	ptMins = [ptMins]
if not isinstance(ptMaxs, list):
	ptMaxs = [ptMaxs]

# load cross sections
inFileCrossSec = TFile.Open(inputCfg['predictions']['crosssec']['filename'])
dirCrossSecPrompt = inFileCrossSec.Get(inputCfg['predictions']['crosssec']['dirnames']['prompt'])
dirCrossSecFD = inFileCrossSec.Get(inputCfg['predictions']['crosssec']['dirnames']['feeddown'])
hCrossSecPrompt = dirCrossSecPrompt.Get(inputCfg['predictions']['crosssec']['histonames']['prompt'])
hCrossSecFD = dirCrossSecFD.Get(inputCfg['predictions']['crosssec']['histonames']['feeddown'])

# load preselection efficiency
if inputCfg['infiles']['preseleff']['filename']:
	infilePreselEff = TFile.Open(inputCfg['infiles']['preseleff']['filename'])
	hPreselEffPrompt = infilePreselEff.Get(inputCfg['infiles']['preseleff']['prompthistoname'])
	hPreselEffFD = infilePreselEff.Get(inputCfg['infiles']['preseleff']['feeddownhistoname'])

# load RAA
RaaPrompt_config = inputCfg['predictions']['Raa']['prompt']
if not isinstance(RaaPrompt_config, float) and not isinstance(RaaPrompt_config, int):
	if not isinstance(RaaPrompt_config, str):
		print('ERROR: RAA must be at least a string or a number. Exit')
		sys.exit()
	else:
		Raa_model_name = inputCfg['predictions']['Raa']['model']
		if Raa_model_name not in ['phsd', 'Catania', 'tamu', 'MCatsHQ']:
			print('ERROR: wrong model name, please check the list of avaliable models. Exit')
			sys.exit()
		else:
			if Raa_model_name == 'phsd':
				RaaPromptSpline, _, ptMinRaaPrompt, ptMaxRaaPrompt = ReadPHSD(RaaPrompt_config)
			elif Raa_model_name == 'Catania':
				RaaPromptSpline, _, ptMinRaaPrompt, ptMaxRaaPrompt = ReadCatania(RaaPrompt_config)
			elif Raa_model_name == 'MCatsHQ':
				RaaPromptSpline, _, ptMinRaaPrompt, ptMaxRaaPrompt = ReadMCatsHQ(RaaPrompt_config)
			elif Raa_model_name == 'tamu':
				RaaPromptSpline, _, ptMinRaaPrompt, ptMaxRaaPrompt = ReadTAMU(RaaPrompt_config)
else:
	RaaPrompt = RaaPrompt_config

RaaFD_config = inputCfg['predictions']['Raa']['feeddown']
if not isinstance(RaaFD_config, float) and not isinstance(RaaFD_config, int):
	if not isinstance(RaaFD_config, str):
		print('ERROR: RAA must be at least a string or a number. Exit')
		sys.exit()
	else:
		Raa_model_name = inputCfg['predictions']['Raa']['model']
		if Raa_model_name not in ['phsd', 'Catania', 'tamu', 'MCatsHQ']:
			print('ERROR: wrong model name, please check the list of avaliable models. Exit')
			sys.exit()
		else:
			if Raa_model_name == 'phsd':
				RaaFDSpline, _, ptMinRaaFD, ptMaxRaaFD = ReadPHSD(RaaFD_config)
			elif Raa_model_name == 'Catania':
				RaaFDSpline, _, ptMinRaaFD, ptMaxRaaFD = ReadCatania(RaaFD_config)
			elif Raa_model_name == 'MCatsHQ':
				RaaFDSpline, _, ptMinRaaFD, ptMaxRaaFD = ReadMCatsHQ(RaaFD_config)
			elif Raa_model_name == 'tamu':
				RaaFDSpline, _, ptMinRaaFD, ptMaxRaaFD = ReadTAMU(RaaFD_config)
else:
	RaaFD = RaaFD_config

if inputCfg['sigma_source'] == 1:
	sigma_file = TFile(inputCfg['sigma_file'], 'read')
	hist_sigma = sigma_file.Get('hRawYieldsSigma')
	hist_sigma.SetDirectory(0)
	hist_mean = sigma_file.Get('hRawYieldsMean')
	hist_mean.SetDirectory(0)
	sigma_file.Close()

# load constant terms
Taa = inputCfg['Taa']
BR = inputCfg['BR']
column_list = inputCfg['column_list']
Bkg_cutvars = inputCfg['cutvars']['ML_output_Bkg']
# set batch mode if enabled
if args.batch:
	gROOT.SetBatch(True)
	gROOT.ProcessLine("gErrorIgnoreLevel = kFatal;")
SetGlobalStyle(padleftmargin=0.12, padrightmargin=0.2, padbottommargin=0.15, padtopmargin=0.075,
			   titleoffset=1., palette=kRainBow, titlesize=0.06, labelsize=0.055, maxdigits=4)
minMass = inputCfg['minMass']
maxMass = inputCfg['maxMass']
bkgConfig = inputCfg['infiles']['background']
nSigmaForSB = bkgConfig['nSigma']
# set batch mode if enabled
if args.batch:
	gROOT.SetBatch(True)
	gROOT.ProcessLine("gErrorIgnoreLevel = kFatal;")
SetGlobalStyle(padleftmargin=0.12, padrightmargin=0.2, padbottommargin=0.15, padtopmargin=0.075,
			   titleoffset=1., palette=kRainBow, titlesize=0.06, labelsize=0.055, maxdigits=4)


def fill_hist(hist_name, df, var, nbins, rebin, scale=False):
	h = TH1F(hist_name, f';{var};NormalisedCounts', nbins, rebin)
	for i in df[var].to_numpy():
		h.Fill(i)
	h.Sumw2()
	if scale:
		h.Scale(1/h.Integral())
	return h

def create_nonuniform_bins(iVarmin, iVarmax, nbins, power=2):
	if iVarmin >= 0:
		
		t = np.linspace(0, 1, nbins + 1)
		nonuniform = t ** power
		nonuniform = nonuniform / nonuniform[-1]
		rebin = iVarmin + (iVarmax - iVarmin) * nonuniform
		return rebin
	
	else:
		
		nbins_pos = nbins // 2  
		nbins_neg = nbins - nbins_pos  
		
		t_pos = np.linspace(0, 1, nbins_pos + 1)
		nonuniform_pos = t_pos ** power
		nonuniform_pos = nonuniform_pos / nonuniform_pos[-1]
		positive_bins = nonuniform_pos * iVarmax
		negative_bins = -np.flip(positive_bins)[:-1]  
		
		rebin = np.concatenate([negative_bins, positive_bins])
		return rebin
def	bin_width_fix(histo):
	for ibin in range(1, histo.GetXaxis().GetNbins()+1):
		width = histo.GetBinWidth(ibin)
		BinContent = histo.GetBinContent(ibin)/width
		BinError = histo.GetBinError(ibin)/width
		histo.SetBinContent(ibin, BinContent)
		histo.SetBinError(ibin,BinError)
	return histo
def calculate_bin_error_sum(hiVarMcPromptPt, hiVarMcFDPt, fPrompt_pt, fFD_pt, ibin):
	# get bin content and their error
	prompt_content = hiVarMcPromptPt.GetBinContent(ibin)
	prompt_error = hiVarMcPromptPt.GetBinError(ibin)
	
	fd_content = hiVarMcFDPt.GetBinContent(ibin)
	fd_error = hiVarMcFDPt.GetBinError(ibin)
	
	# total error
	total_error = np.sqrt((fPrompt_pt * prompt_error)**2 + 
						 (fFD_pt * fd_error)**2)
	
	return total_error

def calculate_bin_error_subtraction(hiVarDataCentPt, hiVarDataSideBandPt, expectedNBKG,expectedBKG_err,expectedNSideBand, ibin):
	content_Center = hiVarDataCentPt.GetBinContent(ibin)
	error_Center = hiVarDataCentPt.GetBinError(ibin)

	content_SideBand = hiVarDataSideBandPt.GetBinContent(ibin)
	error_SideBand = hiVarDataSideBandPt.GetBinError(ibin)
	CountFactor = expectedNBKG/expectedNSideBand
	rel_error_CounterFactor = np.sqrt((expectedBKG_err/expectedNBKG)**2+1/expectedNSideBand)
	if  content_SideBand ==0:
		rel_error_SideBand = 0
	else:
		rel_error_SideBand = error_SideBand/content_SideBand
	rel_error_NormedSideBand = np.sqrt(rel_error_SideBand**2+rel_error_CounterFactor**2)
	error_NormedSideBand = content_SideBand*CountFactor*rel_error_NormedSideBand
	
	
	total_error = np.sqrt(error_Center**2+error_NormedSideBand**2)
	return total_error
# the integral of distribution shape 
def itg(histo):
	Integ = 0
	for ibin in range(1, histo.GetXaxis().GetNbins()+1):
		width = histo.GetBinWidth(ibin)
		BinContent = histo.GetBinContent(ibin)
		Integ += BinContent*width
	return	Integ
pyroot_file = TFile(inputCfg['outfile'], "RECREATE")   
fPrompt, fFD = {}, {}
for iPt, (ptMin, ptMax) in enumerate(zip(ptMins, ptMaxs)):

	folder_name_pt = f"pt_{ptMin}_{ptMax}"
	folder_pt = pyroot_file.Get(folder_name_pt)
	if not folder_pt:
		folder_pt = pyroot_file.mkdir(folder_name_pt)
	folder_pt.cd()
	# if folder_name_pt not in uproot_file.keys():
	#     uproot_file.mkdir(folder_name_pt)

	dfBkgPt = dfBkg_tot.query(f'{ptMin} < fPt  and fPt < {ptMax}')
	# dfSignalFromDataPt = dfBkgPt.query(f'ML_output_Bkg < {Bkg_cutvars[iPt]}')
	dfPromptPt = dfPrompt.query(f'{ptMin} < fPt < {ptMax}')
	dfFDPt = dfFD.query(f'{ptMin} < fPt < {ptMax}')

	# Raa
	ptCent = (ptMax + ptMin) / 2.
	if isinstance(RaaPrompt_config, str):
		if ptMinRaaPrompt < ptCent < ptMaxRaaPrompt:
			RaaPrompt = RaaPromptSpline['yCent'](ptCent)
		elif ptCent > ptMaxRaaPrompt:
			RaaPrompt = RaaPromptSpline['yCent'](ptMaxRaaPrompt)
		else:
			RaaPrompt = RaaPromptSpline['yCent'](ptMinRaaPrompt)
		RaaPrompt = float(RaaPrompt)
	if isinstance(RaaFD_config, str):
		if ptMinRaaFD < ptCent < ptMaxRaaFD:
			RaaFD = RaaFDSpline['yCent'](ptCent)
		elif ptCent > ptMaxRaaFD:
			RaaFD = RaaFDSpline['yCent'](ptMaxRaaFD)
		else:
			RaaFD = RaaFDSpline['yCent'](ptMinRaaFD)
		RaaFD = float(RaaFD)

	# cross section from theory
	ptBinCrossSecMin = hCrossSecPrompt.GetXaxis().FindBin(ptMin*1.0001)
	ptBinCrossSecMax = hCrossSecPrompt.GetXaxis().FindBin(ptMax*0.9999)
	crossSecPrompt = hCrossSecPrompt.Integral(ptBinCrossSecMin, ptBinCrossSecMax, 'width') / (ptMax - ptMin)
	crossSecFD = hCrossSecFD.Integral(ptBinCrossSecMin, ptBinCrossSecMax, 'width') / (ptMax - ptMin)

	# preselection efficiency (if input provided)
	if inputCfg['infiles']['preseleff']['filename']:
		ptBinPreselEff = hPreselEffPrompt.GetXaxis().FindBin(ptMin*1.0001)
		preselEffPrompt = hPreselEffPrompt.GetBinContent(ptBinPreselEff)
		preselEffFD = hPreselEffFD.GetBinContent(ptBinPreselEff)
		preselEffPromptUnc = hPreselEffPrompt.GetBinError(ptBinPreselEff)
		preselEffFDUnc = hPreselEffFD.GetBinError(ptBinPreselEff)
		# print(preselEffFD)
	else:
		preselEffPrompt = 1.
		preselEffFD = 1.

	if inputCfg['sigma_source'] == 0:
		# signal histograms, get sigma and mean from mc
		hMassSignal = TH1F(f'hMassSignal_pT{ptMin}-{ptMax}', ';#it{M} (GeV/#it{c});Counts', 400,
						min(dfPromptPt['fM']), max(dfPromptPt['fM']))
		for mass in np.concatenate((dfPromptPt['fM'].to_numpy(), dfFDPt['fM'].to_numpy())):
			hMassSignal.Fill(mass)
		funcSignal = TF1('funcSignal', SingleGaus, 1.6, 2.2, 3)
		funcSignal.SetParameters(hMassSignal.Integral('width'), hMassSignal.GetMean(), hMassSignal.GetRMS())
		# print(hMassSignal.GetMean(), hMassSignal.GetRMS())
		hMassSignal.Fit('funcSignal', 'Q0')
		mean = funcSignal.GetParameter(1)
		sigma = funcSignal.GetParameter(2)
	elif inputCfg['sigma_source'] == 1:
		sigma = hist_sigma.GetBinContent(iPt+1)
		mean = hist_mean.GetBinContent(iPt+1)
	
	nTotPrompt = len(dfPromptPt)
	nTotFD = len(dfFDPt)
	ML_output_Bkg = inputCfg['cutvars']['ML_output_Bkg'][iPt]
	selToApply = f'ML_output_Bkg<{ML_output_Bkg}'
	if inputCfg['expected_signal_promptness'] == 'nonprompt':
		ML_output_FD = inputCfg['cutvars']['ML_output_FD'][iPt]
		selToApply += f' and ML_output_FD>{ML_output_FD}'
	startTime = time.time()
	dfPromptPtSel = dfPromptPt.query(selToApply)
	dfFDPtSel = dfFDPt.query(selToApply)
	dfBkgPtSel = dfBkgPt.query(selToApply)
	effPrompt, effPromptUnc = ComputeEfficiency(len(dfPromptPtSel), nTotPrompt,
												np.sqrt(len(dfPromptPtSel)), np.sqrt(nTotPrompt))
	effFD, effFDUnc = ComputeEfficiency(len(dfFDPtSel), nTotFD, np.sqrt(len(dfFDPtSel)), np.sqrt(nTotFD))
	effTimesAccPrompt = effPrompt * preselEffPrompt
	effTimesAccFD = effFD * preselEffFD
	fPrompt_pt, fFD_pt = GetPromptFDFractionFc(effTimesAccPrompt, effTimesAccFD,
										crossSecPrompt, crossSecFD, RaaPrompt, RaaFD)
	fPrompt[ptCent] = fPrompt_pt[0]
	fFD[ptCent] = fFD_pt[0]

	# split data to sideband and cent
	lower_bound = mean - nSigmaForSB * sigma
	upper_bound = mean + nSigmaForSB * sigma
	dfBkgPtSel = dfBkgPtSel.copy()
	hMassAll = TH1F(f'hMassAll_pT{ptMin}-{ptMax}', ';#it{M} (GeV/#it{c});Counts', 500,
								min(dfBkgPtSel['fM']), max(dfBkgPtSel['fM']))
	for mass in dfBkgPtSel['fM'].to_numpy():
		hMassAll.Fill(mass)
	hMassAll.Write()
	dfBkgPtSel.loc[:, 'region'] = dfBkgPtSel['fM'].apply(
		lambda x: 'Cent' if lower_bound <= x <= upper_bound else 'SideBand')
	dfDataCentPt = dfBkgPtSel[dfBkgPtSel['region'] == 'Cent']
	dfDataSideBandPt = dfBkgPtSel[dfBkgPtSel['region'] == 'SideBand']
	dfDataSideBandPt = dfDataSideBandPt.query(f'{minMass} < fM < {maxMass}')
	# get expected background cent from side bands
	hMassBkg = TH1F(f'hMassBkg_pT{ptMin}-{ptMax}', ';#it{M} (GeV/#it{c});Counts', 500,
								min(dfBkgPtSel['fM']), max(dfBkgPtSel['fM']))
	for mass in dfDataSideBandPt['fM'].to_numpy():
		hMassBkg.Fill(mass)
	expBkg, errExpBkg = 0, 0
	expBkg, errExpBkg, hMassBkg,funcSB = GetExpectedBkgFromSideBands(hMassBkg, bkgConfig['fitFunc'],
															bkgConfig['nSigma'], mean, sigma,
															0, 0, minMass, maxMass)
	if expBkg==0:
		expBkg, errExpBkg, hMassBkg ,funcSB= GetExpectedBkgFromSideBands(hMassBkg, bkgConfig['fitFunc'],
																bkgConfig['nSigma_backup'][0], mean, sigma,
																0, 0, minMass, maxMass)
	if expBkg==0:
		expBkg, errExpBkg, hMassBkg ,funcSB= GetExpectedBkgFromSideBands(hMassBkg, bkgConfig['fitFunc'],
																bkgConfig['nSigma_backup'][1], mean, sigma,
															 0, 0, minMass, maxMass)
	hMassBkg.Write()
	# CountFactor for scaling sideband to cent
	DataSideBandPtLen = len(dfDataSideBandPt)
	DataCentPtLen = len(dfDataCentPt)
	# DataPtLen = len(dfBkgPtSel)
	CountFactor = (expBkg + DataSideBandPtLen) / DataSideBandPtLen
	S = DataCentPtLen - expBkg
	print(expBkg)
	print(DataSideBandPtLen)
	print(f'DataCentPtLen - expBkg: {S}')
	print(f'CountFactor: {CountFactor}')
	if S < 0:
		# CountFactor = DataCentPtLen / DataSideBandPtLen
		print(f'Warning: Cent region has less entries than expected background from fit')
		print(f'use CountFactor = DataCentPtLen / DataSideBandPtLen: {CountFactor}')
		print(f'expBkg: {expBkg}')
		print(f'dfDataCentPtlen(): {DataCentPtLen}')
		print(f'dfDataSideBandPtlen(): {DataSideBandPtLen}')
	nbins = inputCfg['nbins']
	irebin = 0         
	for iVar in column_list:
		if iVar in ["fM", 'fPt']:
			continue
		print(f'Processing {iVar} for pT {ptMin}-{ptMax}')
		iVarmin, iVarmax = min(min(dfFDPtSel[iVar]), min(dfPromptPtSel[iVar]), min(dfBkgPtSel[iVar])), max(max(dfFDPtSel[iVar]), max(dfPromptPtSel[iVar]), max(dfBkgPtSel[iVar]))
		print(iVarmin, iVarmax)
		if inputCfg['rebin'][iVar]:
			pass
			rebin=inputCfg['rebin'][iVar]
			rebin = np.asarray(rebin, 'd')
			nbins = len(rebin)-1
		elif inputCfg['avg_bin']:
			rebin = np.linspace(iVarmin, iVarmax, nbins + 1)
		else:
			rebin = create_nonuniform_bins(iVarmin, iVarmax, nbins, power=3)
		irebin+=1
		hiVarDataCentPt = fill_hist(f'h{iVar}_pT{ptMin}-{ptMax}_Cent', dfDataCentPt, iVar, nbins, rebin)
		hiVarDataCentPt.Write()
		hiVarDataSideBandPt = fill_hist(f'h{iVar}_pT{ptMin}-{ptMax}_SB', dfDataSideBandPt, iVar, nbins, rebin)
		hiVarDataSideBandPt.Write()

		hiVarDataSignalPt = TH1F(f'h{iVar}_pT{ptMin}-{ptMax}_Signal', f';{iVar};NormalisedCounts', 
								 nbins, rebin)
		for ibin in range(1, hiVarDataSignalPt.GetXaxis().GetNbins()+1):
			BinContent = hiVarDataCentPt.GetBinContent(ibin) - hiVarDataSideBandPt.GetBinContent(ibin) * CountFactor
			hiVarDataSignalPt.SetBinContent(ibin, BinContent)
			BinError = calculate_bin_error_subtraction(hiVarDataCentPt, 
											 hiVarDataSideBandPt,
											 expBkg,errExpBkg,DataSideBandPtLen, ibin)
			hiVarDataSignalPt.SetBinError(ibin, BinError)
		hiVarDataSignalPt = bin_width_fix(hiVarDataSignalPt)
		hiVarDataSignalPt.Scale(1/itg(hiVarDataSignalPt))
		hiVarDataSignalPt.Write()

		# Mc Signal histograms
		hiVarMcPromptPt = fill_hist(f'h{iVar}_pT{ptMin}-{ptMax}_McPrompt', dfPromptPtSel, iVar, nbins, rebin, scale=True)
		hiVarMcPromptPt.Write()

		hiVarMcFDPt = fill_hist(f'h{iVar}_pT{ptMin}-{ptMax}_McFD', dfFDPtSel, iVar, nbins, rebin, scale=True)
		hiVarMcFDPt.Write()

		hiVarMcSignalPt = TH1F(f'h{iVar}_pT{ptMin}-{ptMax}_McSignal', f';{iVar};NormalisedCounts', nbins,
								rebin)

		for ibin in range(1, hiVarMcSignalPt.GetXaxis().GetNbins()+1):
			BinContent = hiVarMcPromptPt.GetBinContent(ibin) * fPrompt_pt[0] + hiVarMcFDPt.GetBinContent(ibin) * fFD_pt[0]
			hiVarMcSignalPt.SetBinContent(ibin, BinContent)
			BinError = calculate_bin_error_sum(hiVarMcPromptPt, hiVarMcFDPt, 
								 fPrompt_pt[0], fFD_pt[0], ibin)
			hiVarMcSignalPt.SetBinError(ibin, BinError)
		hiVarMcSignalPt = bin_width_fix(hiVarMcSignalPt)
		hiVarMcSignalPt.Scale(1/itg(hiVarMcSignalPt))
		hiVarMcSignalPt.Write()

		
		c1 = TCanvas(f"c{iVar}", "Canvas", 1500, 600)
		c1.Divide(2, 1)
		c1.cd(1)
		SetObjectStyle(hiVarDataSignalPt, color=kRed+1, markerstyle=kFullCircle,markersize=1 ,
					   linestyle=7)
		SetObjectStyle(hiVarMcSignalPt, color=kAzure+4, markerstyle=kOpenSquare, 
					   markersize=1, linewidth=1, linestyle=7)
		
		hiVarMcSignalPt.Draw("P E")
		hiVarDataSignalPt.Draw("P E same")
		maxy = max(hiVarDataSignalPt.GetMaximum(), hiVarMcSignalPt.GetMaximum())
		miny = min(hiVarDataSignalPt.GetMinimum(), hiVarMcSignalPt.GetMinimum())
		hiVarDataSignalPt.GetYaxis().SetRangeUser(miny, maxy*1.1)
		hiVarMcSignalPt.GetYaxis().SetRangeUser(miny, maxy*1.1)
		c1.GetPad(1).SetLogy()
		leg = TLegend(0.65, 0.7, 0.85, 0.85)
		leg.SetTextSize(0.025)
		leg.SetFillStyle(0)
		leg.AddEntry(hiVarMcSignalPt, "Mc", "p")
		leg.AddEntry(hiVarDataSignalPt, "Data", "p")
		leg.Draw()
		
		c1.cd(2)
		hiVarRatio = hiVarDataSignalPt.Clone(f"hiVarRatio_{iVar}")
		hiVarRatio.Divide(hiVarMcSignalPt)
		maxy = min(hiVarRatio.GetMaximum(), 2)
		miny = min(hiVarRatio.GetMinimum(), -0.1)
		hiVarRatio.SetMaximum(maxy*1.1)
		hiVarRatio.SetMinimum(miny)
		hiVarRatio.GetYaxis().SetRangeUser(-0.1, 2.2)
		hiVarRatio.SetTitle(f";{iVar};Data/Mc")
		
		hiVarRatio.Draw("P E0")
		
		c1.Write()
	c0 = TCanvas("c_hmass", "Canvas", 800, 600)
	SetObjectStyle(funcSB,olor = kRed)
	hMassAll.Draw()
	funcSB.Draw("same")
	c0.Write()


hist_fPrompt = TH1F("hfPrompt", "Prompt Fraction", len(fPrompt), np.asarray(ptLims, 'd'))
hist_fFD = TH1F("hfFD", "Feed-Down Fraction", len(fFD), np.asarray(ptLims, 'd'))
SetObjectStyle(hist_fPrompt, color=kRed+1, markerstyle=kFullCircle)
SetObjectStyle(hist_fFD, color=kAzure+4, markerstyle=kOpenSquare, markersize=1.5, linewidth=2, linestyle=7)
for iPt, (_, value) in enumerate(fPrompt.items()):
	hist_fPrompt.SetBinContent(iPt + 1, value) 
	hist_fPrompt.SetBinError(iPt + 1, 0)
for iPt, (_, value) in enumerate(fFD.items()):
	hist_fFD.SetBinContent(iPt + 1, value)
	hist_fFD.SetBinError(iPt + 1, 0)


pyroot_file.cd()
leg = TLegend(0.6, 0.2, 0.8, 0.4)
leg.SetTextSize(0.035)
leg.SetFillStyle(0)
leg.AddEntry(hist_fPrompt, "Prompt", "p")
leg.AddEntry(hist_fFD, "Feed-down", "p")
nPtBins = len(ptMins)
cFrac = TCanvas('cFrac', '', 800, 800)
cFrac.DrawFrame(ptMins[0], 1.e-5, ptMaxs[nPtBins-1], 1.,
			   ';#it{p}_{T} (GeV/#it{c});Fraction;')
hist_fPrompt.Draw('P Esame')
hist_fFD.Draw('P E same')
leg.Draw()
hist_fPrompt.Write()
hist_fFD.Write()
cFrac.Write()
pyroot_file.Close()
# if not args.batch:
#     input('Press enter to exit')
