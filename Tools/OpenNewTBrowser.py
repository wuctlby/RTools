import sys
import os

import ROOT

def main():
    if len(sys.argv) < 2:
        print("Error: ROOT file path is required.")
        return
    
    filepath = sys.argv[1]
    print(f"Opening ROOT file: {filepath}")
    
    root_file = ROOT.TFile.Open(filepath)
    if not root_file or root_file.IsZombie():
        print(f"Error: Failed to open file '{filepath}'")
        return
    
    browser = ROOT.TBrowser("MyBrowser", root_file)
    
    if not ROOT.gROOT.IsBatch():
        ROOT.gApplication.Run()

if __name__ == "__main__":
    main()