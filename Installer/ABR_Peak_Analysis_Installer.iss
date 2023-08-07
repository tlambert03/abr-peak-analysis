; -- sync.iss --

; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!
#define verStr GetFileVersion("..\Source\dist\notebook\notebook.exe")
#define lastDot RPos(".", verStr)
#define verStr Copy(verStr, 1, lastDot-1)
#define verStr_ StringChange(verStr, '.', '-')

[Setup]
AppName=ABR Peak Analysis
AppVerName=ABR Peak Analysis V{#verStr}
DefaultDirName={pf}\EPL\ABR Peak Analysis
OutputDir=D:\Development\abr-peak-analysis\Installer\Output
DefaultGroupName=EPL
AllowNoIcons=yes
OutputBaseFilename=ABR_Peak_Analysis_{#verStr_}
UsePreviousAppDir=no
UsePreviousGroup=no
DisableProgramGroupPage=yes
PrivilegesRequired=lowest

[Files]
Source: "..\Source\dist\notebook\*.*"; DestDir: "{app}"; Excludes: "*.dll.c~,\mpl-data\fonts,\mpl-data\sample_data"; Flags: replacesameversion recursesubdirs; 

[Icons]
Name: "{commondesktop}\ABR Peak Analysis"; Filename: "{app}\notebook.exe"; IconFilename: "{app}\icon.ico"; IconIndex: 0
