vim ~/.local/share/applications/root-tbrowser.desktop

[Desktop Entry]
Version=1.0
Type=Application
Name=ROOT TBrowser
Exec=gnome-terminal -- bash /home/wuct/ALICE/local/RTools/RTools/Tools/Linux/OpenNewTBrowser.sh %f
Icon=root
Terminal=false
MimeType=application/x-root;
Categories=Science;

update-desktop-database ~/.local/share/applications
gio mime application/x-root root-tbrowser.desktop