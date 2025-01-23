vim ~/.local/share/applications/root-tbrowser.desktop

[Desktop Entry]
Version=1.0
Type=Application
Name=ROOT TBrowser
Exec=gnome-terminal -- bash -c 'python3 /home/wuct/ALICE/local/RTools/RTools/Tools/OpenNewTBrowser.py "%f"; exit'
Icon=root
Terminal=false
MimeType=application/x-root;
Categories=Science;

update-desktop-database ~/.local/share/applications
gio mime application/x-root root-tbrowser.desktop