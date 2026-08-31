; Kill UI + backend before install/uninstall (backend locks resources/*.exe).
!macro KillIflowMcpCatalogFleetProcesses
  DetailPrint "Stopping iflow-mcp-catalog processes..."
  ExecWait 'taskkill /F /IM iflow-mcp-catalog-backend.exe /T' $0
  ExecWait 'taskkill /F /IM iflow-mcp-catalog-native.exe /T' $0
  !if "${INSTALLMODE}" == "currentUser"
    nsis_tauri_utils::KillProcessCurrentUser "iflow-mcp-catalog-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcessCurrentUser "iflow-mcp-catalog-native.exe"
    Pop $0
  !else
    nsis_tauri_utils::KillProcess "iflow-mcp-catalog-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcess "iflow-mcp-catalog-native.exe"
    Pop $0
  !endif
  Sleep 2000
!macroend

!macro NSIS_HOOK_PREINSTALL
  !insertmacro KillIflowMcpCatalogFleetProcesses
!macroend

!macro NSIS_HOOK_PREUNINSTALL
  !insertmacro KillIflowMcpCatalogFleetProcesses
!macroend

!macro NSIS_HOOK_POSTINSTALL
  IfFileExists "$INSTDIR\resources\install-mcp-clients.ps1" 0 mcp_hook_done
    DetailPrint "Optional: register iflow-mcp-catalog in Cursor / Claude Desktop"
    ExecWait 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$INSTDIR\resources\install-mcp-clients.ps1" -Interactive'
  mcp_hook_done:
!macroend
