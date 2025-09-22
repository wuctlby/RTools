#%%
import argparse
import shlex
import os

def main(String):
    bash_safe_string = shlex.quote(String)
    os.system(f'bash /home/wuct/ALICE/reps/RTools/Linux/src/OpenNewTBrowser.sh {bash_safe_string}')

#%%
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("String", metavar="text",
                        default="path/to/file.root", help="input ROOT file")
    args = parser.parse_args()

    main(
        String=args.String
        )