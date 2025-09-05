#!/bin/bash

BASH_DIR=$(dirname "$0")
Target_Bash_Dir=$(realpath "$BASH_DIR/../src/OpenNewTBrowser.sh")
echo "Target Bash Script: $Target_Bash_Dir"

cat << EOL > ~/.local/share/applications/root-tbrowser.desktop
[Desktop Entry]
Version=1.0
Type=Application
Name=ROOT TBrowser
Exec=gnome-terminal -- bash "$Target_Bash_Dir" %f
Icon=utilities-terminal
Terminal=false
# MIME type for ROOT files, used to associate .root files with this application
MimeType=application/x-root;
Categories=Science;
EOL
update-desktop-database ~/.local/share/applications
gio mime application/x-root root-tbrowser.desktop