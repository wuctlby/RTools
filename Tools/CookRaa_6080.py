import numpy as np
import pandas as pd

fileNameTAMU = "/home/wuct/localAnalysis/flow/DmesonAnalysis/models/tamu/B_TAMU_RAA_5TeV_3050.txt" 

dfTAMU = pd.read_csv(fileNameTAMU, sep=' ', comment='#')

#dfTAMU['R_AA'] = (dfTAMU['R_AA_min'] + dfTAMU['R_AA_max']) / 2

Raa_6080 = []
output_file_path = "/home/wuct/localAnalysis/flow/DmesonAnalysis/models/tamu/B_TAMU_RAA_5TeV_6080.txt"
with open(output_file_path, "w") as output_file:
    for i, pt in enumerate(dfTAMU['PtCent']):
        gap = (dfTAMU['R_AA'][i] - 1) / 2
        Raa_6080.append(1+gap)
        output_file.write(f'{pt} {Raa_6080[i]}\n')