; 考种平台 Inno Setup 安装脚本
; 自动安装应用程序和驱动

#define MyAppName "SeedTest"
#define MyAppVersion "2.0"
#define MyAppPublisher "JinLab"
#define MyAppURL "https://github.com/xianjunhong/SeedTest"
#define MyAppExeName "SeedTest.exe"

[Setup]
; 基本信息
AppId={{A1B2C3D4-E5F6-4A5B-9C8D-7E6F5A4B3C2D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=INSTALL_NOTES.txt
OutputDir=installer_output
OutputBaseFilename=SeedTest_v{#MyAppVersion}_Setup
;SetupIconFile=icons\app_icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
;Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "installmvs"; Description: "Install Hikvision Camera Driver (MVS SDK)"; GroupDescription: "Drivers:"; Flags: checkedonce
Name: "installpl23xx"; Description: "Install Serial Port Driver (PL23XX)"; GroupDescription: "Drivers:"; Flags: checkedonce

[Files]
; 主程序文件
Source: "dist\SeedTest\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; 驱动安装包
Source: "MVS_STD_4.4.0_240913.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Tasks: installmvs
Source: "PL23XX-M_LogoDriver_Setup_408_20220725.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Tasks: installpl23xx
; 文档 (如果文件不存在则注释掉)
;Source: "readme.md"; DestDir: "{app}"; Flags: ignoreversion
;Source: "使用说明.md"; DestDir: "{app}"; Flags: ignoreversion
;Source: "快速开始.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
;Name: "{group}\User Manual"; Filename: "{app}\User_Manual.md"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Install drivers silently during installation (takes time, please wait)
Filename: "{tmp}\MVS_STD_4.4.0_240913.exe"; Parameters: "/S"; StatusMsg: "Installing Hikvision Camera Driver (This may take 3-5 minutes)..."; Flags: waituntilterminated; Tasks: installmvs
Filename: "{tmp}\PL23XX-M_LogoDriver_Setup_408_20220725.exe"; Parameters: "/S"; StatusMsg: "Installing Serial Port Driver..."; Flags: waituntilterminated; Tasks: installpl23xx
; Launch program after installation
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
  if not IsAdminLoggedOn() then
  begin
    MsgBox('This installer requires administrator privileges to install drivers.' + #13#10 + 
           'Please right-click the installer and select "Run as administrator".', 
           mbError, MB_OK);
    Result := False;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // 创建数据目录
    if not DirExists(ExpandConstant('{app}\data')) then
      CreateDir(ExpandConstant('{app}\data'));
    if not DirExists(ExpandConstant('{app}\data\images')) then
      CreateDir(ExpandConstant('{app}\data\images'));
    if not DirExists(ExpandConstant('{app}\data\processed')) then
      CreateDir(ExpandConstant('{app}\data\processed'));
    if not DirExists(ExpandConstant('{app}\data\acquisition')) then
      CreateDir(ExpandConstant('{app}\data\acquisition'));
  end;
end;


