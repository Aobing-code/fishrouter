!include "MUI2.nsh"

Name "FishRouter"
OutFile "FishRouter-Setup.exe"
InstallDir "$PROGRAMFILES64\FishRouter"
RequestExecutionLevel admin

!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Section "Install"
  SetOutPath "$INSTDIR"
  File "FishRouter.exe"
  File "fishrouter-server.exe"
  File "config.json"
  File "README.md"

  CreateDirectory "$SMPROGRAMS\FishRouter"
  CreateShortCut "$SMPROGRAMS\FishRouter\FishRouter.lnk" "$INSTDIR\FishRouter.exe"
  CreateShortCut "$DESKTOP\FishRouter.lnk" "$INSTDIR\FishRouter.exe"

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FishRouter" "DisplayName" "FishRouter"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FishRouter" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FishRouter" "InstallLocation" "$INSTDIR"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FishRouter" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FishRouter" "NoRepair" 1

  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\*.*"
  RMDir "$INSTDIR"
  Delete "$SMPROGRAMS\FishRouter\FishRouter.lnk"
  RMDir "$SMPROGRAMS\FishRouter"
  Delete "$DESKTOP\FishRouter.lnk"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FishRouter"
SectionEnd
