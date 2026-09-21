#define AppName "IP Scanner"
#define AppVersion "1.1.0"
#define AppExeName "IP Scanner.exe"

[Setup]
AppId={{60AD403D-5F76-4D90-A634-F150F60892DC}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Ramrattan Network Tools
DefaultDirName={localappdata}\Programs\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\..\dist
OutputBaseFilename=IP-Scanner-Windows-x64-1.1.0
SetupIconFile=..\..\build\windows-icon\IPScanner.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#AppExeName}
CloseApplications=yes

[Files]
Source: "..\..\dist\IP Scanner\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{userdesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent

; Scan history and schedule settings live in the user's Documents folder and
; intentionally remain available after repair, upgrade, or uninstall.
