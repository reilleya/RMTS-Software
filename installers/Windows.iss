[Setup]
AppName=RMTS
AppVersion=1.0.0
WizardStyle=modern
DefaultDirName={autopf}\RMTS
DefaultGroupName=RMTS
UninstallDisplayIcon={app}\RMTS.exe
Compression=lzma2
SolidCompression=yes

[Files]
Source: "../dist/RMTS/*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\RMTS"; Filename: "{app}\RMTS.exe"
