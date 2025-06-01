import yaml
import os

mc_files = [
    "/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/flow/MC/AnalysisResults_full_default_407164.root",
    "/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/flow/MC/AnalysisResults_full_ptsmearing1p5_407162.root",
    "/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/flow/MC/AnalysisResults_full_ptsmearing1p5_vsphi_407161.root",
]

track_tuner_lables = [
    "default",
    "ptsmearing1p5",
    "ptsmearing1p5_vsphi"
]

addtional_lables = "_full"

config_file = "/home/wuct/ALICE/local/DmesonAnalysis/run3/flow/config/2024/k3050/config_flow_pass4_mc.yml"

for iFile, mc_file in enumerate(mc_files):
    print(f'Processing {mc_file}')
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    config['eff_filename'] = mc_file
    config['suffix'] = f"{track_tuner_lables[iFile]}{addtional_lables}"
    
    new_file_path = config_file.replace('.yml', f'_{track_tuner_lables[iFile]}{addtional_lables}.yml')
    
    with open(new_file_path, 'w') as out_file:
        yaml.dump(config, out_file)
        print('New config file created:', new_file_path)