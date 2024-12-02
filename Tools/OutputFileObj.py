from ROOT import TFile
import ROOT
import os
import argparse
#inputFile = '/home/wuct/localAnalysis/flow/DmesonAnalysis/run3/tool/Optimization/Data_D0_test.root'
#inputFile = '/home/wuct/localAnalysis/flow/DmesonAnalysis/run3/tool/Optimization/Data_D0_test1.root'
# inputFile = '/home/wuct/data/flow/2060/MC/AnalysisResults_fakeML.root'
# inputFile ="/home/wuct/localAnalysis/flow/DmesonAnalysis/run3/tool/pTweight/genptshape/ptweights/DzeroPbPb/PtWeigths_LHC24g2b.root"
# inputFile = '/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/ML/MC/AO2D_MC_293770_small.root'



def traverse_directory(directory, path="", output_file=None):
    for key in directory.GetListOfKeys():
        obj = key.ReadObj()
        obj_name = obj.GetName()
        current_path = os.path.join(path, obj_name)
        
        if obj.IsA().InheritsFrom(ROOT.TDirectory.Class()):
            # If the object is a directory, traverse it recursively
            traverse_directory(obj, current_path, output_file)

        elif obj.IsA().InheritsFrom(ROOT.TTree.Class()):
            for leaf in obj.GetListOfLeaves():
                leaf_name = leaf.GetName()
                leaf_path = os.path.join(current_path, leaf_name)
                if output_file:
                    output_file.write(f'"{leaf_path}"\n')
                    print(f'"{leaf_path}"')
        else:
            # If the object is not a directory, write its path and name to the file
            if output_file:
                output_file.write(f'"{current_path}"\n')
                print(f'"{current_path}"')

def main(inputFile):
    # 打开ROOT文件
    infile = TFile(inputFile)

    # 打开输出文件
    output_file_path = "/home/wuct/ALICE/local/DmesonAnalysis/RTools/Tools/output.txt"

    if os.path.exists(output_file_path):
        with open(output_file_path, 'a') as output_file:
            output_file.write(f'"{inputFile}"\n')
            traverse_directory(infile, output_file=output_file)
    else:
        with open(output_file_path, 'w') as output_file:
            output_file.write(f'"{inputFile}"\n')
        # 遍历ROOT文件中的所有一级文件夹
        traverse_directory(infile, output_file=output_file)

    # 关闭ROOT文件
    infile.Close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("inputFile", metavar="text",
                        default="an_res.root", help="input ROOT file")
    args = parser.parse_args()

    main(
        inputFile=args.inputFile
        )