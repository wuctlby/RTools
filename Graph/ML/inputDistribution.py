import os
import sys
import ROOT
import yaml
import numpy as np
import argparse
import matplotlib.pyplot as plt

from hipe4ml import plot_utils
from hipe4ml.tree_handler import TreeHandler

ROOT.gROOT.SetBatch(True)

def cook_labels(labels, prompt=True):
    if prompt:
        return [f"{label}_Prompt" for label in labels]
    else:
        return [f"{label}_FD" for label in labels]

def check_origin(label):
    if 'Prompt' in label:
        return 'Prompt'
    elif 'FD' in label:
        return 'FD'
    else:
        raise ValueError("Label must contain either 'Prompt' or 'FD'.")

def reflection_filter(df, pureSig=True):
    if pureSig:
        return df[(df['fCandidateSelFlag'] == 1) & (df['fFlagMcMatchRec'] == 1) | (df['fCandidateSelFlag'] == 2) & (df['fFlagMcMatchRec'] == -1)]
    else:
        return df[(df['fCandidateSelFlag'] == 1) & (df['fFlagMcMatchRec'] == -1) | (df['fCandidateSelFlag'] == 2) & (df['fFlagMcMatchRec'] == 1)]

def plot_ditribution(dfs, vars, numerator=[0], denominator=[1], output_path=None, pt_bin=None, filters={'Prompt':{}, 'FD':{}}, legend_labels=None, entry=True):
    if len(numerator) != len(denominator):
        raise ValueError("Numerator and denominator lists must have the same length.")
    if len(numerator) == 0 or len(denominator) == 0:
        raise ValueError("Numerator and denominator lists cannot be empty.")

    n_vars = len(vars)
    ncols = 4
    nrows = (n_vars + ncols - 1) // ncols
    fig_dis, axes_dis = plt.subplots(nrows, ncols, figsize=(16, 9))
    fig_ratio, axes_ratio = plt.subplots(nrows, ncols, figsize=(16, 9))
    axes_dis = axes_dis.flatten()
    axes_ratio = axes_ratio.flatten()
    for idx, var in enumerate(vars):
        histograms = []
        bin_centers = []
        for i, df in enumerate(dfs):
            
            # reflection filter
            if filters['reflection_filter']:
                df = reflection_filter(df, pureSig=True)

            normalizer = len(df['fPt'])

            ori = check_origin(legend_labels[i])

            if var in filters[ori]:
                df = df[(df[var] > filters[ori][var][0]) & (df[var] < filters[ori][var][1])]
                hist, bins = np.histogram(df[var], bins=filters[ori][var][2], range=[filters[ori][var][0], filters[ori][var][1]], 
                                          density=False, weights=[1.0 / normalizer / (filters[ori][var][1] - filters[ori][var][0] / filters[ori][var][2])] * len(df[var]))
            elif var == 'fPt':
                df = df[(df[var] > pt_bin[0]) & (df[var] < pt_bin[1])]
                hist, bins = np.histogram(df[var], bins=10, range=[pt_bin[0], pt_bin[1]], 
                                          density=False, weights=[1.0 / normalizer / (pt_bin[1] - pt_bin[0] / 10)] * len(df[var]))
            elif var == 'fPtProng0' or var == 'fPtProng1':
                df = df[(df[var] > 0) & (df[var] < pt_bin[1])]
                hist, bins = np.histogram(df[var], bins=10, range=[0, pt_bin[1]], 
                                          density=False, weights=[1.0 / normalizer / (pt_bin[1] / 10)] * len(df[var]))
            # elif var == 'fM':
            #     hist, bins = np.histogram(df[var], bins=120, range=[1.55, 2.25],
            #                               density=False)
            else:
                bin_width = (df[var].max() - df[var].min()) / 100 if df[var].max() > df[var].min() else 1.0
                hist, bins = np.histogram(df[var], bins=100, range=[df[var].min(), df[var].max()],
                                          density=False, weights=[1.0 / normalizer / bin_width] * len(df[var]))

            bin_centers.append(0.5 * (bins[:-1] + bins[1:]))
            histograms.append(hist)
            axes_dis[idx].step(bin_centers[i], histograms[i], where='mid', label=legend_labels[i] if legend_labels else f"Dataset {i}")
        axes_dis[idx].set_title(f'{var}')
        axes_dis[idx].set_yscale('log')
        
        for iRatio, (num, denom) in enumerate(zip(numerator, denominator)):
            ratio = np.divide(histograms[num], histograms[denom], out=np.zeros_like(histograms[num], dtype=float), where=histograms[denom] != 0)
            # ratio = np.nan_to_num(ratio, nan=0.0, posinf=2.0, neginf=0.0)
            label = f"{legend_labels[num]} / {legend_labels[denom]}" if legend_labels else f"Ratio {num} / {denom}"
            axes_ratio[idx].step(bin_centers[num], ratio, where='mid', label=label)
            axes_ratio[idx].set_ylim(0.5, 1.5)
        axes_ratio[idx].set_title(f'{var}')
        axes_ratio[idx].axhline(1, color='red', linestyle='--')
        
        if idx == len(vars) - 1:
            axes_dis[idx].legend()
            axes_ratio[idx].legend()
    
    # plot the candidates number for each case
    if entry:
        if filters['reflection_filter']:
            entries = [len(reflection_filter(df, pureSig=True)) for df in dfs]
        for iDf, df in enumerate(dfs):
            label = f'{entries[iDf]}'
            axes_dis[len(vars)].bar(iDf, entries[iDf], label=label)
        axes_dis[len(vars)].set_title("Entries")
        axes_dis[len(vars)].legend()

        for iRatio, (num, denom) in enumerate(zip(numerator, denominator)):
            ratio_entry = entries[num] / entries[denom] if entries[denom] != 0 else 0
            label = f'{entries[num]} / {entries[denom]}'
            axes_ratio[len(vars)].bar(iRatio, ratio_entry, label=label)
        axes_ratio[len(vars)].set_title("Entries Ratio")
        axes_ratio[len(vars)].legend()
    filled_axes = len(vars) + 1 if entry else len(vars)
    for j in range(filled_axes, len(axes_dis)):
        fig_dis.delaxes(axes_dis[j])
        fig_ratio.delaxes(axes_ratio[j])
    
    fig_dis.subplots_adjust(left=0.06, bottom=0.06, right=0.99, top=0.96, hspace=0.55, wspace=0.20)
    fig_dis.suptitle(f"pT: {pt_bin[0]} - {pt_bin[1]}", fontsize=20, y=0.99)
    fig_ratio.subplots_adjust(left=0.06, bottom=0.06, right=0.99, top=0.96, hspace=0.55, wspace=0.20)
    fig_ratio.suptitle(f"pT: {pt_bin[0]} - {pt_bin[1]}", fontsize=20, y=0.99)

    if output_path:
        fig_dis.savefig(output_path)
        prefix = output_path.split('/')[-1].split('_')[1]
        fig_ratio.savefig(output_path.replace(f'{prefix}', f'{prefix}_ratio'))
    plt.close('all')

def store_inv_mass(dfs, output_path=None, legend_labels=None, filters={}):
    root_histograms = []
    for i, df in enumerate(dfs):
        ori = check_origin(legend_labels[i])

        hist_origin, bins_origin = np.histogram(df['fM'], bins=filters[ori]['fM'][2], 
                                                range=[filters[ori]['fM'][0], filters[ori]['fM'][1]],
                                                density=False)
        root_hist_origin = ROOT.TH1D("hInvMassOrigin", "Invariant Mass Origin", len(bins_origin)-1, bins_origin)
        for j in range(len(hist_origin)):
            root_hist_origin.SetBinContent(j+1, hist_origin[j]+1)
        root_hist_origin.SetTitle(f"Invariant Mass Origin - {legend_labels[i] if legend_labels else f'Dataset {i}'}")
        root_hist_origin.SetName(f"hist_inv_mass_origin_{legend_labels[i]}" if legend_labels else f"hist_inv_mass_origin_{i}")
        root_histograms.append(root_hist_origin)

        # store the invariant mass of reflection
        if filters['reflection_filter']:
            df_ref = reflection_filter(df, pureSig=False)
            df = reflection_filter(df, pureSig=True)
            
        hist, bins = np.histogram(df['fM'], bins=filters[ori]['fM'][2], 
                                  range=[filters[ori]['fM'][0], filters[ori]['fM'][1]],
                                  density=False)
        if filters['reflection_filter']:
            hist_ref, bins_ref = np.histogram(df_ref['fM'], bins=100,
                                            range=[filters[ori]['fM'][0], filters[ori]['fM'][1]],
                                            density=False)
        hist_bkg, bins_bkg = np.histogram(np.array(range(len(df['fM']))), bins=filters[ori]['fM'][2], 
                                          range=[filters[ori]['fM'][0], filters[ori]['fM'][1]],
                                          density=False)

        binwidth = bins[1] - bins[0]
        
        # Convert numpy histogram to ROOT histogram
        root_hist = ROOT.TH1D("hInvMass", "Invariant Mass", len(bins)-1, bins)
        root_hist_bkg = ROOT.TH1D("hInvMassBkg", "Invariant Mass Background", len(bins_bkg)-1, bins_bkg)
        bkg = np.zeros_like(hist_bkg)
        for j in range(len(hist)):
            root_hist.SetBinContent(j+1, hist[j])
            root_hist_bkg.SetBinContent(j+1, bkg[j]+1)
        root_hist.SetTitle(f"Invariant Mass - {legend_labels[i] if legend_labels else f'Dataset {i}'}")
        root_hist.SetName(f"hist_inv_mass_{legend_labels[i]}" if legend_labels else f"hist_inv_mass_{i}")
        root_hist_bkg.SetTitle(f"Invariant Mass Background - {legend_labels[i] if legend_labels else f'Dataset {i}'}")
        root_hist_bkg.SetName(f"hist_inv_mass_bkg_{legend_labels[i]}" if legend_labels else f"hist_inv_mass_bkg_{i}")
        root_histograms.append(root_hist_bkg)
        
        gaus = ROOT.TF1("gaus", "gaus", 1.45, 2.25)
        root_hist.Fit(gaus, "Q")  # "Q" for quiet mode
        root_histograms.append(root_hist)

        if filters['reflection_filter']:
            root_hist_ref = ROOT.TH1D("hInvMass_ref", "Invariant Mass Reflection", len(bins_ref)-1, bins_ref)
            for j in range(len(hist_ref)):
                root_hist_ref.SetBinContent(j+1, hist_ref[j])
            root_hist_ref.SetTitle(f"Invariant Mass Reflection - {legend_labels[i] if legend_labels else f'Dataset {i}'}")
            root_hist_ref.SetName(f"hist_inv_mass_ref_{legend_labels[i]}" if legend_labels else f"hist_inv_mass_ref_{i}")
            
            double_gaus = ROOT.TF1("double_gaus", "gaus(0) + gaus(3)", 1.65, 2.15)
            double_gaus.SetParameters(gaus.GetParameter(0), gaus.GetParameter(1), gaus.GetParameter(2),
                                    gaus.GetParameter(0), gaus.GetParameter(1) + 0.1, gaus.GetParameter(2))
            root_hist_ref.Fit(double_gaus, "Q")  # "Q" for quiet mode
            root_histograms.append(root_hist_ref)

    # Write the ROOT histogram to a file
    out_file = ROOT.TFile(output_path, "RECREATE")
    for hist in root_histograms:
        hist.Write()
    out_file.Close()

def main(config):
    
    # Load the configuration file
    with open(config, 'r') as file:
        cfg = yaml.safe_load(file)
    
    prompt_files = cfg['input']['prompt']
    fd_files = cfg['input']['FD']
    tree_name = cfg['input']['treename']
    
    outputDir = cfg['output']['output_dir']
    suffix = cfg['output']['suffix']
    if '_' not in suffix and suffix != '':
        suffix = '_' + suffix
    
    pt_min = cfg['pt_ranges']['min']
    pt_max = cfg['pt_ranges']['max']
    variables_to_plot = cfg['plots']['plotting_columns']
    filters = cfg['filters']
    leg_labels = cook_labels(cfg['plots']['leg_labels']['Prompt'], prompt=True) + \
                    cook_labels(cfg['plots']['leg_labels']['FD'], prompt=False)
    
    # load the prompt and FD trees
    prompt_handlers, fd_handlers = [], []
    for iFile, (prompt_file, fd_file) in enumerate(zip(prompt_files, fd_files)):
        prompt_handlers.append(TreeHandler(prompt_file, tree_name))
        fd_handlers.append(TreeHandler(fd_file, tree_name))

    # slice the trees
    pt_bins = [[a, b] for a, b in zip(pt_min, pt_max)]
    for prompt_handler, fd_handler in zip(prompt_handlers, fd_handlers):
        # Ensure the trees are sliced by fPt
        prompt_handler.slice_data_frame('fPt', pt_bins, True)
        fd_handler.slice_data_frame('fPt', pt_bins, True)
    
    outDir = os.path.join(outputDir, f'input{suffix}')
    
    for iPtBin, pt_bin in enumerate(pt_bins):
        print(f"Processing pt bin {iPtBin} with range {pt_bin}")

        if cfg['func']['inputDistr']:
            os.makedirs(os.path.join(outDir, 'Distr'), exist_ok=True)
            os.makedirs(os.path.join(outDir, 'Distr_normalized'), exist_ok=True)        
            
            # all distributions and ratios
            list_df = [
                prompt_handlers[i].get_slice(iPtBin) for i in range(len(prompt_handlers))
            ] + [
                fd_handlers[i].get_slice(iPtBin) for i in range(len(fd_handlers))
            ]

            plot_ditribution(
                list_df, variables_to_plot, [0, 2], [1, 3],
                output_path=f'{outDir}/Distr/All_pT_{pt_bin[0]}_{pt_bin[1]}{suffix}.png',
                pt_bin=pt_bin,
                filters=filters,
                legend_labels=leg_labels,
                entry=True
            )

            plot_utils.plot_distr(list_df, variables_to_plot, 100, leg_labels, figsize=(12, 7),
                            alpha=0.3, log=False, grid=False, density=True)
            plt.subplots_adjust(left=0.06, bottom=0.06, right=0.99, top=0.96, hspace=0.55, wspace=0.55)
            plt.savefig(f'{outDir}/Distr_normalized/All_pT_{pt_bin[0]}_{pt_bin[1]}{suffix}.png')
            plt.close('all')

            # plot the ratio of prompt and FD separately
            list_df_prompt = [
                prompt_handlers[i].get_slice(iPtBin) for i in range(len(prompt_handlers))
            ]
            list_df_fd = [
                fd_handlers[i].get_slice(iPtBin) for i in range(len(fd_handlers))
            ]

            plot_ditribution(
                list_df_prompt, variables_to_plot, [0], [1],
                output_path=f'{outDir}/Distr/Prompt_pT_{pt_bin[0]}_{pt_bin[1]}{suffix}.png',
                pt_bin=pt_bin,
                filters=filters,
                legend_labels=cook_labels(cfg['plots']['leg_labels']['Prompt'], prompt=True),
                entry=True
            )
            plot_ditribution(
                list_df_fd, variables_to_plot, [0], [1],
                output_path=f'{outDir}/Distr/FD_pT_{pt_bin[0]}_{pt_bin[1]}{suffix}.png',
                pt_bin=pt_bin,
                filters=filters,
                legend_labels=cook_labels(cfg['plots']['leg_labels']['FD'], prompt=False),
                entry=True
            )
            
            plot_utils.plot_distr(list_df_prompt, variables_to_plot, 100, cfg['plots']['leg_labels']['Prompt'],
                                figsize=(12, 7), alpha=0.25, log=False, grid=False, density=True)
            plt.subplots_adjust(left=0.06, bottom=0.06, right=0.99, top=0.96, hspace=0.55, wspace=0.55)
            plt.savefig(f'{outDir}/Distr_normalized/Prompt_pT_{pt_bin[0]}_{pt_bin[1]}{suffix}.png')
            plt.close('all')
            plot_utils.plot_distr(list_df_fd, variables_to_plot, 100, cfg['plots']['leg_labels']['FD'],
                                figsize=(12, 7), alpha=0.25, log=False, grid=False, density=True)
            plt.subplots_adjust(left=0.06, bottom=0.06, right=0.99, top=0.96, hspace=0.55, wspace=0.55)
            plt.savefig(f'{outDir}/Distr_normalized/FD_pT_{pt_bin[0]}_{pt_bin[1]}{suffix}.png')
            plt.close('all')

        if cfg['func']['storeInvMass']:
            os.makedirs(os.path.join(outDir, 'InvMass'), exist_ok=True)

            # inherit the list_df from the previous step
            if not cfg['func']['inputDistr']:
                list_df = [
                    prompt_handlers[i].get_slice(iPtBin) for i in range(len(prompt_handlers))
                ] + [
                    fd_handlers[i].get_slice(iPtBin) for i in range(len(fd_handlers))
                ]
            
            store_inv_mass(
                list_df, 
                output_path=f'{outDir}/InvMass/InvMass_pT_{pt_bin[0]}_{pt_bin[1]}{suffix}.root',
                legend_labels=leg_labels, 
                filters=filters
            )
            
        if cfg['func']['reflection']:
            os.makedirs(os.path.join(outDir, 'Reflection'), exist_ok=True)
            # inherit the list_df from the previous step
            if not cfg['func']['inputDistr']:
                list_df = [
                    prompt_handlers[i].get_slice(iPtBin) for i in range(len(prompt_handlers))
                ] + [
                    fd_handlers[i].get_slice(iPtBin) for i in range(len(fd_handlers))
                ]
            
            for i, df in enumerate(list_df):
                df_sig = df[(df['fCandidateSelFlag'] == 1) & (df['fFlagMcMatchRec'] == 1) | (df['fCandidateSelFlag'] == 2) & (df['fFlagMcMatchRec'] == -1)]
                df_ref = df[(df['fCandidateSelFlag'] == 1) & (df['fFlagMcMatchRec'] == -1) | (df['fCandidateSelFlag'] == 2) & (df['fFlagMcMatchRec'] == 1)]
                print(f"{leg_labels[i] if leg_labels else f'Dataset {i}'}\t\t- Total: {len(df)}, \t- Signal: {len(df_sig)}, \tReflection: {len(df_ref)}")
                # print(f"Dataset {i} - Total: {len(df)}, Signal: {len(df_sig)}, Reflection: {len(df_ref)}")

    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("config", metavar="text",
                        default="config_inputDistr.yaml", help="Configuration file")
    args = parser.parse_args()

    main(
        config=args.config
    )
