#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: $0 <ROOT_FILE>"
  exit 1
fi

if [[ "$1" != *.root ]]; then
    echo "Error: The file must be a ROOT file."
    exit 1
fi

cd "$(dirname "$1")" || exit 1
root --web=off -l -e "TFile::Open(\"$1\"); new TBrowser(\"$1\");"

exit 0