#!/bin/bash
if [ $# -ne 1 ]; then
  echo "Usage: $0 <TAG>"
  exit 1
fi

TAG="$1"
TAG_FILE=~/.proc_tags

# get the process group ID (PGID) from the tag file
PGID=$(grep "^$TAG:" $TAG_FILE | cut -d: -f2)

if [ -z "$PGID" ]; then
  echo "❌ didn't find the tag: $TAG"
  exit 1
fi

# kill the process group by PGID
if ! kill -0 -$PGID 2>/dev/null; then
  echo "❌ Process group $PGID is not running."
  exit 1
fi
kill -9 -$PGID 2>/dev/null

# remove the tag from the file
sed -i "/^$TAG:/d" $TAG_FILE
echo "✅ Killed process group: $TAG (PGID:$PGID)"