#!/bin/bash
if [ $# -lt 1 ]; then
  echo "Usage: $0 <TAG> <COMMAND> [ARGS...]"
  exit 1
fi

TAG="$1"
shift 

# set the tag for the process
setsid /bin/bash -c "$*" &
PARENT_PID=$!

# get the process group ID (PGID) of the parent process
PGID=$(ps -o pgid= $PARENT_PID | grep -o '[0-9]*')

# store the tag and PGID in file
echo "$TAG:$PGID" >> ~/.proc_tags

echo "▶️ Running! [TAG: $TAG] [PGID: $PGID]"