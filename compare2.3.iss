[Setup]
AppName=Compare
AppVersion=2.3
AppPublisher=Crabapple
DefaultDirName={autopf}\Compare
DefaultGroupName=Compare
AllowNoIcons=yes
OutputDir=Output
OutputBaseFilename=CompareInstaller
SetupIconFile=compare.ico
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
ShowLanguageDialog=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "chinese"; MessagesFile: "Chinese.isl"

[Files]
Source: "dist\compare.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "compare.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{commondesktop}\Compare"; Filename: "{app}\compare.exe"; IconFilename: "{app}\compare.ico"
Name: "{group}\Compare"; Filename: "{app}\compare.exe"
Name: "{group}\Uninstall Compare"; Filename: "{uninstallexe}"

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
    ValueType: string; ValueName: "Compare"; \
    ValueData: "{app}\compare.exe"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Crabapple\Compare"; \
    ValueType: string; ValueName: "Language"; ValueData: {language}; \
    Flags: uninsdeletekey

[Run]
Filename: "{app}\compare.exe"; Description: "{cm:LaunchProgram,Compare}"; \
    Flags: shellexec postinstall skipifsilent

[Code]
// 声明Windows API函数
function GetDiskFreeSpaceEx(lpDirectoryName: String; var FreeBytesAvailableToCaller,
  TotalNumberOfBytes, TotalNumberOfFreeBytes: Int64): Boolean;
external 'GetDiskFreeSpaceExW@kernel32.dll stdcall';

function NextButtonClick(CurPageID: Integer): Boolean;
var
  Drive: String;
  FreeBytesAvailable, TotalBytes, TotalFreeBytes: Int64;
begin
  Result := True;
  
  // 磁盘空间检查
  if CurPageID = wpSelectDir then
  begin
    Drive := AddBackslash(ExtractFileDrive(ExpandConstant('{app}')));
    
    if GetDiskFreeSpaceEx(Drive, FreeBytesAvailable, TotalBytes, TotalFreeBytes) then
    begin
      if FreeBytesAvailable < 1024 * 1024 * 1024 then  // 1024 MB = 1 GB
      begin
        if ActiveLanguage = 'chinese' then
          MsgBox('安装需要至少 1024MB 可用空间！驱动器：' + Drive + #13#10 +
                 '当前可用空间: ' + IntToStr(FreeBytesAvailable div (1024 * 1024)) + ' MB', 
                 mbError, MB_OK)
        else
          MsgBox('Installation requires at least 1024MB of free space! Drive: ' + Drive + #13#10 +
                 'Available space: ' + IntToStr(FreeBytesAvailable div (1024 * 1024)) + ' MB', 
                 mbError, MB_OK);
        Result := False;
      end;
    end
    else
    begin
      if ActiveLanguage = 'chinese' then
        MsgBox('无法检测驱动器 ' + Drive + ' 的可用空间', mbError, MB_OK)
      else
        MsgBox('Unable to detect free space on drive ' + Drive, mbError, MB_OK);
      Result := False;
    end;
  end;
end;

function InitializeUninstall(): Boolean;
var
  Language: String;
begin
  // 从注册表读取安装时选择的语言
  if RegQueryStringValue(HKEY_CURRENT_USER, 'Software\Crabapple\Compare', 'Language', Language) then
  begin
    if Language = 'chinese' then
      Result := MsgBox('确定要卸载 Compare 吗？', mbConfirmation, MB_YESNO) = IDYES
    else
      Result := MsgBox('Are you sure you want to uninstall Compare?', mbConfirmation, MB_YESNO) = IDYES;
  end
  else
  begin
    // 如果注册表中没有记录，默认使用英文
    Result := MsgBox('Are you sure you want to uninstall Compare?', mbConfirmation, MB_YESNO) = IDYES;
  end;
end;
