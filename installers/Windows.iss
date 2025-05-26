[Setup]
AppName=RMTS
AppVersion=0.4.0
WizardStyle=modern
DefaultDirName={autopf}\RMTS
DefaultGroupName=RMTS
UninstallDisplayIcon={app}\RMTS.exe
Compression=lzma2
SolidCompression=yes
AlwaysRestart=yes

[Files]
Source: "../dist/RMTS/*"; DestDir: "{app}"; Flags: recursesubdirs
Source: "driver/CDM21228_Setup.exe"; DestDir: "{app}"; AfterInstall: RunOtherInstaller

[Code]
procedure RunOtherInstaller;
var
  ResultCode: Integer;
begin
  if not Exec(ExpandConstant('{app}\CDM21228_Setup.exe'), '', '', SW_SHOWNORMAL, ewWaitUntilTerminated, ResultCode)
  then
    MsgBox('Other installer failed to run!' + #13#10 + SysErrorMessage(ResultCode), mbError, MB_OK);
end;

[Icons]
Name: "{group}\RMTS"; Filename: "{app}\RMTS.exe"

[Registry]
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Services\sermouse"; ValueType: dword; ValueName: "Start"; ValueData: "4";
