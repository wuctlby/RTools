import os
import sys
import ROOT
import yaml
import numpy as np
import argparse
import matplotlib.pyplot as plt

from hipe4ml import plot_utils
from hipe4ml.tree_handler import TreeHandler

from utils import cook_labels, store_inv_mass, plot_ditribution
ROOT.gROOT.SetBatch(True)

def main(config):
    
    if isinstance(config, str):
    # Load the configuration file
        with open(config, 'r') as file:
            cfg = yaml.safe_load(file)
    elif isinstance(config, dict):
        cfg = config
    
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
    
    # global return
    sig_components_pt = {}
    
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
            sig_components = {}
            for i, df in enumerate(list_df):
                # df_sig = df[(df['fCandidateSelFlag'] == 1) & (df['fFlagMcMatchRec'] == 1) | (df['fCandidateSelFlag'] == 2) & (df['fFlagMcMatchRec'] == -1)]
                # df_ref = df[(df['fCandidateSelFlag'] == 1) & (df['fFlagMcMatchRec'] == -1) | (df['fCandidateSelFlag'] == 2) & (df['fFlagMcMatchRec'] == 1)]
                # print(f"{leg_labels[i] if leg_labels else f'Dataset {i}'}\t\t- Total: {len(df)}, \t- Signal: {len(df_sig)}, \tReflection: {len(df_ref)}")
                # print(f"Dataset {i} - Total: {len(df)}, Signal: {len(df_sig)}, Reflection: {len(df_ref)}")
                
                # only reconstructed as D0 or D0bar, and it is matched with MC
                df_pure_sig = df[(df['fCandidateSelFlag'] == 4) & (df['fFlagMcMatchRec'] == 1) | (df['fCandidateSelFlag'] == 8) & (df['fFlagMcMatchRec'] == -1)]
                # only reconstructed as D0 or D0bar, and it is not matched with MC
                df_pure_ref = df[(df['fCandidateSelFlag'] == 4) & (df['fFlagMcMatchRec'] == -1) | (df['fCandidateSelFlag'] == 8) & (df['fFlagMcMatchRec'] == 1)]
                
                # reconstructed as D0 and D0bar, and it is matched with MC
                df_ref_sig = df[(df['fCandidateSelFlag'] == 1) & (df['fFlagMcMatchRec'] == 1) | (df['fCandidateSelFlag'] == 2) & (df['fFlagMcMatchRec'] == -1)]
                # reconstructed as D0 and D0bar, and it is not matched with MC
                df_ref_ref = df[(df['fCandidateSelFlag'] == 1) & (df['fFlagMcMatchRec'] == -1) | (df['fCandidateSelFlag'] == 2) & (df['fFlagMcMatchRec'] == 1)]
                
                print(f"{leg_labels[i]} f'pure_signal: {len(df_pure_sig)}, \ref_signal: {len(df_ref_sig)}, \ref_ref: {len(df_ref_ref)}, \tpure_ref: {len(df_pure_ref)}, \ttotal: {len(df)}")
                sig_components[i] = {
                    'pure_signal': df_pure_sig,
                    'ref_signal': df_ref_sig,
                    'ref_ref': df_ref_ref,
                    'pure_ref': df_pure_ref,
                    'total': df
                }
                for icomp, df_comp in sig_components[i].items():
                    mask = (df_comp['fNSigTpcTofPiExpPi'] > 3) | (df_comp['fNSigTpcTofKaExpKa'] > 3)
                    if not df_comp[mask].empty:
                        colors = {
                            'pure_signal': '\033[92m',  # green
                            'ref_signal': '\033[94m',   # blue
                            'ref_ref': '\033[93m',      # yellow
                            'pure_ref': '\033[91m',     # red
                            'total': '\033[0m'          # reset/no color
                        }
                        color = colors.get(icomp, '\033[0m')
                        reset = '\033[0m'
                        print(
                            f"{color}Warning: {icomp} has {len(df_comp[mask])} entries outside [-inf, 3] range: "
                            f"fNSigTpcTofPiExpPi: {df_comp[mask]['fNSigTpcTofPiExpPi'].values} "
                            f"fNSigTpcTofKaExpKa: {df_comp[mask]['fNSigTpcTofKaExpKa'].values}{reset}"
                        )
                        
            sig_components_pt[iPtBin] = sig_components
    if cfg['func']['reflection']:
        return sig_components_pt
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("config", metavar="text",
                        default="config_inputDistr.yaml", help="Configuration file")
    args = parser.parse_args()

    main(
        config=args.config
    )
