import os
import sys
import ROOT
import yaml
import numpy as np
import argparse
import matplotlib.pyplot as plt

from hipe4ml import plot_utils
from hipe4ml.tree_handler import TreeHandler

def cook_labels(labels, prompt=True):
    if prompt:
        return [f"{label}_Prompt" for label in labels]
    else:
        return [f"{label}_FD" for label in labels]
    
def plot_ditribution(dfs, vars, numerator=[0], denominator=[1], output_path=None, pt_bin=None, filters={'Prompt':{}, 'FD':{}}, legend_labels=None, entry=True):
    if len(numerator) != len(denominator):
        raise ValueError("Numerator and denominator lists must have the same length.")
    if len(numerator) == 0 or len(denominator) == 0:
        raise ValueError("Numerator and denominator lists cannot be empty.")
    
    root_histograms = []
    
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
            normalizer = len(df['fPt'])

            if 'Prompt' in legend_labels[i]:
                ori = "Prompt"
            elif 'FD' in legend_labels[i]:
                ori = "FD"
            else:
                print('Error: No prompt or FD in legend labels')

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
            elif var == 'fM':
                hist, bins = np.histogram(df[var], bins=120, range=[1.55, 2.25],
                                          density=False)

            # fit for fM
            # if var == 'fM':
            #     # Convert numpy histogram to ROOT histogram
            #     root_hist = ROOT.TH1D("h1", "h1", len(bins)-1, bins)
            #     binwidth = bins[1] - bins[0]
            #     for j in range(len(hist)):
            #         root_hist.SetBinContent(j+1, hist[j] / binwidth)
                
            #     # Perform the fit
            #     gaus = ROOT.TF1("gaus", "gaus", 1.45, 2.25)
            #     root_hist.Fit(gaus, "Q")  # "Q" for quiet mode
            #     root_hist.SetTitle(f"Fit for {var} - {legend_labels[i] if legend_labels else f'Dataset {i}'}")
            #     root_hist.SetName(f"hist_{var}_{legend_labels[i]}")
            #     root_histograms.append(root_hist)

            bin_centers.append(0.5 * (bins[:-1] + bins[1:]))
            histograms.append(hist)
            axes_dis[idx].step(bin_centers[i], histograms[i], where='mid', label=legend_labels[i] if legend_labels else f"Dataset {i}")
            
        axes_dis[idx].set_title(f'{var}')
        
        for iRatio, (num, denom) in enumerate(zip(numerator, denominator)):
            ratio = np.divide(histograms[num], histograms[denom], out=np.zeros_like(histograms[num], dtype=float), where=histograms[denom] != 0)
            # ratio = np.nan_to_num(ratio, nan=0.0, posinf=2.0, neginf=0.0)
            label = f"{legend_labels[num]} / {legend_labels[denom]}" if legend_labels else f"Ratio {num} / {denom}"
            axes_ratio[idx].step(bin_centers[num], ratio, where='mid', label=label)
            axes_ratio[idx].set_ylim(0.5, 1.5)
        axes_ratio[idx].axhline(1, color='red', linestyle='--')
        
        if idx == len(vars) - 1:
            axes_dis[idx].legend()
            axes_ratio[idx].legend()
    
    # plot the candidates number for each case
    if entry:
        entries = [len(df['fPt']) for df in dfs]
        for iAxis, ax in enumerate(axes_dis):
            label = f'{entries[iAxis]}'
            ax.bar(iAxis, entries[iAxis], label=label)
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
    fig_ratio.subplots_adjust(left=0.06, bottom=0.06, right=0.99, top=0.96, hspace=0.55, wspace=0.20)
    if output_path:
        fig_dis.savefig(output_path)
        fig_ratio.savefig(output_path.replace('.png', '_ratio.png'))
    plt.close('all')
    
    root_file = ROOT.TFile(output_path.replace('.png', '.root').replace('Distribution_', 'Histograms_'), 'RECREATE')
    for hist in root_histograms:
        hist.Write()
    root_file.Close()

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
    
    for iPtBin, pt_bin in enumerate(pt_bins):
        print(f"Processing pt bin {iPtBin} with range {pt_bin}")
        outDir = f'{outputDir}/input{suffix}'
        os.makedirs(outDir, exist_ok=True)
        
        # all distributions and ratios
        list_df = [
            prompt_handlers[i].get_slice(iPtBin) for i in range(len(prompt_handlers))
        ] + [
            fd_handlers[i].get_slice(iPtBin) for i in range(len(fd_handlers))
        ]

        plot_ditribution(
            list_df, variables_to_plot, [0, 2], [1, 3],
            output_path=f'{outDir}/Distribution_pT_{pt_bin[0]}_{pt_bin[1]}{suffix}.png',
            pt_bin=pt_bin,
            
            legend_labels=leg_labels,
            entry=True
        )

        plt.subplots_adjust(left=0.06, bottom=0.06, right=0.99, top=0.96, hspace=0.55, wspace=0.55)
        plt.savefig(f'{outputDir}/Distr/All_pT_{pt_bin[0]}_{pt_bin[1]}{suffix}.png')
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
            legend_labels=cook_labels(cfg['plots']['leg_labels']['Prompt'], entry=True)
        )
        plot_ditribution(
            list_df_fd, variables_to_plot, [0], [1],
            output_path=f'{outDir}/Distr/FD_pT_{pt_bin[0]}_{pt_bin[1]}{suffix}.png',
            pt_bin=pt_bin,
            legend_labels=cook_labels(cfg['plots']['leg_labels']['FD'], entry=False)
        )
        
        plot_utils.plot_distr(list_df_prompt, variables_to_plot, 100, cfg['plots']['leg_labels']['Prompt'],
                              figsize=(12, 7), alpha=0.25, log=False, grid=False, density=True)
        plt.subplots_adjust(left=0.06, bottom=0.06, right=0.99, top=0.96, hspace=0.55, wspace=0.55)
        plt.savefig(f'{outputDir}/Distr_normalized/Prompt_pT_{pt_bin[0]}_{pt_bin[1]}{suffix}.png')
        plt.close('all')
        plot_utils.plot_distr(list_df_fd, variables_to_plot, 100, cfg['plots']['leg_labels']['FD'],
                              figsize=(12, 7), alpha=0.25, log=False, grid=False, density=True)
        plt.subplots_adjust(left=0.06, bottom=0.06, right=0.99, top=0.96, hspace=0.55, wspace=0.55)
        plt.savefig(f'{outputDir}/Distr_normalized/FD_pT_{pt_bin[0]}_{pt_bin[1]}{suffix}.png')
        plt.close('all')

    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("config", metavar="text",
                        default="config_inputDistr.yaml", help="Configuration file")
    args = parser.parse_args()

    main(
        config=args.config
    )
