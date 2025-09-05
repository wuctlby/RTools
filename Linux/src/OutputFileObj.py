from ROOT import TFile
import ROOT
import os
import argparse
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

def traverse_directory(directory, path="", output_file=None):
    for key in directory.GetListOfKeys():
        obj = key.ReadObj()
        obj_name = key.GetName()
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
        elif obj.IsA().InheritsFrom(ROOT.THnSparse.Class()):
            obj
            for iAxis in range(obj.GetNdimensions()):
                axis_name = obj.GetAxis(iAxis).GetTitle()
                axis_path = os.path.join(current_path, axis_name) + f" axis{iAxis}"
                if output_file:
                    output_file.write(f'"{axis_path}"\n')
                    print(f'"{axis_path}"')
        else:
            # If the object is not a directory, write its path and name to the file
            if output_file:
                output_file.write(f'"{current_path}"\n')
                print(f'"{current_path}"')

def main(inputFile):
    infile = TFile(inputFile)

    output_file_path = "/tmp/obj_output.txt"

    with open(output_file_path, 'w') as output_file:
        output_file.write(f'"{inputFile}"\n')

    if os.path.exists(output_file_path):
        with open(output_file_path, 'a') as output_file:
            output_file.write(f'"{inputFile}"\n')
            traverse_directory(infile, output_file=output_file)
    else:
        
        with open(output_file_path, 'w') as output_file:
            output_file.write(f'"{inputFile}"\n')
        traverse_directory(infile, output_file=output_file)

    infile.Close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("inputFile", metavar="text",
                        default="an_res.root", help="input ROOT file")
    args = parser.parse_args()

    main(
        inputFile=args.inputFile
        )