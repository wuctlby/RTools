#!/bin/bash

BASH_DIR=$(dirname "$0")

cat << EOL > ~/.local/share/applications/root-tbrowser.desktop
[Desktop Entry]
Version=1.0
Type=Application
Name=ROOT TBrowser
Exec=gnome-terminal -- bash /home/wuct/ALICE/reps/RTools/Linux/src/OpenNewTBrowser.sh %f
Icon=utilities-terminal
Terminal=false
# MIME type for ROOT files, used to associate .root files with this application
MimeType=application/x-root;
Categories=Science;
EOL
update-desktop-database ~/.local/share/applications
gio mime application/x-root root-tbrowser.desktop