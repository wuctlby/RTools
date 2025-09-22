#!/bin/bash

# source $HOME/Software/root/bin/thisroot.sh

if [ $# -lt 1 ]; then
  echo "Usage: $0 <ROOT_FILE>"
  exit 1
fi

if [[ "$1" != *.root ]]; then
    echo "Error: The file must be a ROOT file."
    exit 1
fi

(
  source $HOME/Software/root/bin/thisroot.sh
  cd "$(dirname "$1")" || exit 1
  root --web=off -l -e "TFile::Open(\"$1\"); new TBrowser(\"$1\");"
)

# cd "$(dirname "$1")" || exit 1
# root --web=off -l -e "TFile::Open(\"$1\"); new TBrowser(\"$1\");"

# while true; do
#     read -rp "Do you want to close the terminal? (y/n): " yn
#     case $yn in
#         [Yy]* ) break;;
#         [Nn]* ) echo "Keeping the terminal open. Type 'exit' to close it."; bash;;
#         * ) echo "Please answer yes or no.";;
#     esac
# done

exit 0